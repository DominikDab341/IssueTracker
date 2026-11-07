"""Import 120 approved English references; never create synthetic user tickets."""
import argparse
import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.domain import ACTIVE_TASK_STATES
from app.models.models import ClassificationReference, ClassificationTask, Ticket
from app.services.classifier import classify, get_model
from app.services.priorities import update_effective_priority
from app.services.text_validation import validate_ticket_text
from app.settings import settings
from scripts.evaluate_pilot import select_labels, validate_dataset

SOURCE = "pilot_en_120_v1"
DATASET = Path(__file__).resolve().parent.parent / "data/pilot/tickets.en.json"
engine = create_async_engine(settings.DATABASE_URL)


def approved_references(path=DATASET):
    dataset = json.loads(path.read_text(encoding="utf-8"))
    examples = validate_dataset(dataset)
    if dataset["language"] != "en":
        raise ValueError("Referencja operacyjna wymaga języka angielskiego.")
    selected = select_labels([row for row in examples if row.get("reference_eligible", True)], "reviewed")
    if len(selected) != 120:
        raise ValueError("Wersja pilot_en_120_v1 wymaga dokładnie 120 zatwierdzonych referencji.")
    return selected


async def seed_tickets():
    references = approved_references()
    async with AsyncSession(engine) as session:
        await session.execute(text("SELECT pg_advisory_xact_lock(49011203)"))
        existing = {row.source_key: row for row in (await session.scalars(
            select(ClassificationReference).where(ClassificationReference.source == SOURCE))).all()}
        if set(existing) - {row["id"] for row in references}:
            raise ValueError("Baza zawiera inne referencje pod tą samą wersją; utwórz nową wersję.")
        for row in references:
            previous = existing.get(row["id"])
            if previous and (previous.text, previous.category, previous.base_priority) != (
                    row["text"], row["category"], row["base_priority"]):
                raise ValueError("Zmieniono zatwierdzone etykiety lub tekst; utwórz nową wersję referencji.")
        missing = [row for row in references if row["id"] not in existing]
        if not missing:
            print("120 English references already imported; user tickets unchanged.")
            return
        descriptions = [validate_ticket_text(row["text"]) for row in missing]
        model = get_model()
        for row, description in zip(missing, descriptions):
            session.add(ClassificationReference(text=description, category=row["category"],
                                                base_priority=row["base_priority"],
                                                embedding_vector=model.encode(description).tolist(),
                                                source=SOURCE, source_key=row["id"]))
        await session.commit()
        print(f"Imported {len(missing)} approved English references. No user tickets created.")


async def reclassify_legacy():
    """Run with API stopped; preserve status, authors, manual decisions and old labels."""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        if settings.CLASSIFICATION_REFERENCE_SOURCE != SOURCE:
            raise ValueError("Najpierw aktywuj źródło pilot_en_120_v1.")
        ids = list(await session.scalars(select(Ticket.id).where(
            Ticket.legacy_category.is_not(None), Ticket.category == "unknown")))
        count = 0
        for ident in ids:
            ticket = await session.scalar(select(Ticket).where(Ticket.id == ident).with_for_update())
            if ticket.category != "unknown":
                await session.rollback()
                continue
            active = await session.scalar(select(ClassificationTask.id).where(
                ClassificationTask.ticket_id == ident, ClassificationTask.state.in_(ACTIVE_TASK_STATES)))
            if active:
                raise ValueError("Istnieją aktywne zadania; zakończ je przed przeklasyfikowaniem historii.")
            prediction = await classify(ticket.text, session)
            if prediction.category == "unknown":
                raise ValueError("Brak aktywnych referencji; najpierw wykonaj import.")
            ticket.predicted_category = ticket.category = prediction.category
            ticket.predicted_category_version = ticket.content_version
            ticket.base_priority = prediction.base_priority
            ticket.automatic_priority = prediction.automatic_priority
            ticket.classification_version = prediction.classification_version
            ticket.embedding_vector, ticket.embedding_version = prediction.vector, ticket.content_version
            update_effective_priority(ticket)
            await session.commit()
            count += 1
        print(f"Reclassified {count} legacy tickets; original labels retained in legacy_category.")


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reclassify-legacy", action="store_true",
                        help="Przeklasyfikuj stare kategorie; uruchom przy zatrzymanym API.")
    args = parser.parse_args()
    try:
        await seed_tickets()
        if args.reclassify_legacy:
            await reclassify_legacy()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
