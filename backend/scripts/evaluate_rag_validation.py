"""Run both RAG rankers through the chat handler on an empty, migrated test database."""

import argparse
import asyncio
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from time import perf_counter
from unittest.mock import patch

import httpx
from fastapi import HTTPException
from sqlalchemy import exists, select, text
from sqlalchemy.ext.asyncio import AsyncSession

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.api import assistant as chat_api
from app.database.database import engine
from app.models.models import Ticket, User
from app.services.access import Role
from app.services.assistant import PROMPT_VERSION, SYSTEM_PROMPT, PreviousTurn, generate_answer
from app.services.classifier import get_model
from app.services.ticket_search import SearchMethod, reload_ticket_sources, search_tickets
from app.settings import settings


async def seed_corpus(db, tickets):
    if await db.scalar(text("SELECT current_database()")) != "issuetracker_test":
        raise RuntimeError("Use the issuetracker_test database.")
    if await db.scalar(select(exists().select_from(Ticket) | exists().select_from(User))):
        raise RuntimeError("Use a test database with no existing tickets or users.")
    actor = User(id=1, email="validation@example.invalid", password_hash="not-a-login-hash",
                 role=Role.STAFF, is_approved=True, approved_at=datetime.now(timezone.utc))
    db.add(actor)
    await db.flush()
    vectors = get_model().encode([row["problem"] for row in tickets]).tolist()
    for row, vector in zip(tickets, vectors, strict=True):
        resolution = row.get("resolution")
        db.add(Ticket(id=row["id"], text=row["problem"], resolution_note=resolution,
                      status="resolved" if resolution else "reported", author_id=actor.id,
                      priority="medium", category="unknown", embedding_vector=vector, embedding_version=1))
    await db.commit()


async def run_case(db, method, case, previous):
    trace = {"source_ids": [], "model_status": None}

    async def search(*args, **kwargs):
        result = await search_tickets(*args, method=method, **kwargs)
        trace.update(source_ids=[hit.id for hit in result.hits], source_mode="search",
                     embedding_ms=result.embedding_ms, search_ms=result.search_ms)
        return result

    async def reload(*args, **kwargs):
        hits = await reload_ticket_sources(*args, **kwargs)
        trace.update(source_ids=[hit.id for hit in hits[:chat_api.SOURCE_LIMIT]], source_mode="history")
        return hits

    async def generate(question, history, hits, previous_turns):
        started = perf_counter()
        try:
            answer = await generate_answer(question, history, hits, previous_turns)
            trace["model_status"] = answer.status
            return answer
        finally:
            trace["generation_ms"] = (perf_counter() - started) * 1000

    actor = await db.get(User, 1)
    request = chat_api.ChatRequest(
        question=case["question"], previous_turns=[previous] if previous else [],
        resolved_only=case.get("resolved_only", True),
    )
    started = perf_counter()
    with patch.object(chat_api, "search_tickets", search), \
         patch.object(chat_api, "reload_ticket_sources", reload), \
         patch.object(chat_api, "generate_answer", generate):
        try:
            response = await chat_api.chat(request, actor, db)
            result = {"response": response.model_dump()}
        except HTTPException as exc:
            result = {"error": {"status": exc.status_code, "detail": exc.detail}}
    return {"case": case["id"], "previous_turns": [turn.model_dump() for turn in request.previous_turns],
            **trace, **result, "total_ms": (perf_counter() - started) * 1000}


async def run_method(connection, method, cases):
    rows = []
    turns = {}
    for case in cases:
        async with AsyncSession(bind=connection, join_transaction_mode="create_savepoint") as db:
            row = await run_case(db, method, case, turns.get(case.get("follows")))
        response = row.get("response")
        if response is not None:
            turns[case["id"]] = PreviousTurn(question=case["question"], parts=response["parts"])
        expected = set(case["relevant_ids"])
        if expected and "follows" not in case:
            ids = row["source_ids"]
            row["recall"] = len(expected.intersection(ids)) / len(expected)
            row["reciprocal_rank"] = next((1 / rank for rank, key in enumerate(ids, 1) if key in expected), 0)
        rows.append(row)
        print(f'{method} {case["id"]}: {row["source_ids"]} ({row["total_ms"]:.0f} ms)', flush=True)
    scored = [row for row in rows if "recall" in row]
    return {"recall_at_k": mean(row["recall"] for row in scored),
            "mrr_at_k": mean(row["reciprocal_rank"] for row in scored), "cases": rows}


async def evaluate(path):
    raw = path.read_bytes()
    data = json.loads(raw)
    # Refuse an implicit connection to the normal application database.
    if engine.url.database != "issuetracker_test":
        raise RuntimeError("Set DATABASE_URL to the dedicated issuetracker_test database.")
    async with httpx.AsyncClient(trust_env=False, timeout=10) as client:
        tags = await client.get(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags")
        tags.raise_for_status()
    digest = next(model["digest"] for model in tags.json()["models"] if model["name"] == settings.OLLAMA_MODEL)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            async with AsyncSession(bind=connection, join_transaction_mode="create_savepoint") as db:
                await seed_corpus(db, data["tickets"])
            results = {method: await run_method(connection, method, data["cases"]) for method in SearchMethod}
        finally:
            await transaction.rollback()
    return {
        "dataset": path.name,
        "dataset_sha256": hashlib.sha256(raw).hexdigest(),
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "application_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "k": chat_api.SOURCE_LIMIT,
        "semantic_min_similarity": settings.RAG_MIN_SIMILARITY,
        "embedding_model": settings.MODEL_NAME,
        "embedding_revision": settings.MODEL_REVISION,
        "ollama_model": settings.OLLAMA_MODEL,
        "ollama_model_digest": digest,
        "prompt_version": PROMPT_VERSION,
        "prompt_sha256": hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        "results": results,
    }


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/rag/validation-en-v1.json")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = await evaluate(args.dataset)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
