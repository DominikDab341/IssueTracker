"""Compare both application rankers on a fixed, isolated English pilot."""
import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from statistics import mean, median
from types import SimpleNamespace
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text

from app.database.database import async_session, engine
from app.services.access import Role
from app.services.classifier import get_model
from app.services.ticket_search import SearchMethod, search_tickets
from app.settings import settings


async def evaluate(path: Path, limit: int, repeats: int) -> dict:
    raw = path.read_bytes()
    data = json.loads(raw)
    actor = SimpleNamespace(role=Role.STAFF, is_active=True, is_approved=True)
    started = perf_counter()
    model = get_model()
    model_load_ms = (perf_counter() - started) * 1000
    vectors = model.encode([ticket["problem"] for ticket in data["tickets"]]).tolist()
    async with async_session() as db, db.begin():
        await db.execute(text("""
            CREATE TEMP TABLE tickets (
                id integer PRIMARY KEY, text text NOT NULL, status text NOT NULL,
                resolution_note text, content_version integer NOT NULL DEFAULT 1,
                embedding_version integer NOT NULL DEFAULT 1, embedding_vector vector(384) NOT NULL
            ) ON COMMIT DROP
        """))
        await db.execute(text("""
            INSERT INTO pg_temp.tickets (id, text, status, resolution_note, embedding_vector)
            VALUES (:id, :problem, :status, :resolution, CAST(:vector AS vector))
        """), [
            dict(id=row["id"], problem=row["problem"], vector=json.dumps(vector),
                 resolution=row.get("resolution"), status="resolved" if row.get("resolution") else "reported")
            for row, vector in zip(data["tickets"], vectors, strict=True)
        ])
        await db.execute(text("""
            CREATE INDEX ON pg_temp.tickets USING gin (to_tsvector('english'::regconfig, text))
        """))
        await db.execute(text("ANALYZE pg_temp.tickets"))
        results = {}
        for method in SearchMethod:
            rows = []
            await search_tickets(db, actor, data["questions"][0]["question"], method=method, limit=limit)
            for case in data["questions"]:
                runs = [await search_tickets(db, actor, case["question"], method=method, limit=limit)
                        for _ in range(repeats)]
                found = [hit.id for hit in runs[0].hits]
                expected = set(case["relevant_ids"])
                rows.append({
                    **case,
                    "retrieved_ids": found,
                    "recall": len(set(found) & expected) / len(expected) if expected else None,
                    "reciprocal_rank": next((1 / rank for rank, ident in enumerate(found, 1) if ident in expected), 0)
                    if expected else None,
                    "median_embedding_ms": median(run.embedding_ms for run in runs),
                    "median_search_ms": median(run.search_ms for run in runs),
                    "median_total_ms": median(run.embedding_ms + run.search_ms for run in runs),
                })
            answerable = [row for row in rows if row["relevant_ids"]]
            results[method] = {
                "recall_at_k": mean(row["recall"] for row in answerable),
                "mrr_at_k": mean(row["reciprocal_rank"] for row in answerable),
                "empty_results_on_unanswerable": sum(not row["retrieved_ids"] for row in rows if not row["relevant_ids"]),
                "median_total_ms": median(row["median_total_ms"] for row in rows),
                "questions": rows,
            }
    return {
        "dataset": path.name, "dataset_sha256": hashlib.sha256(raw).hexdigest(), "tickets": len(data["tickets"]),
        "k": limit, "repeats": repeats, "resolved_only": True, "indexed_field": "problem",
        "embedding_model": settings.MODEL_NAME, "embedding_revision": settings.MODEL_REVISION,
        "model_load_ms": model_load_ms, "semantic_min_similarity": settings.RAG_MIN_SIMILARITY,
        "full_text_config": "english", "results": results,
    }


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/rag/pilot-en.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.limit < 1 or args.repeats < 1:
        parser.error("limit and repeats must be positive")
    try:
        report = await evaluate(args.dataset, args.limit, args.repeats)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
