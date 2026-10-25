import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from app.models.models import ClassificationReference, Ticket
from app.services.classifier import get_model
from app.services.text_validation import validate_ticket_text

engine = create_async_engine(settings.DATABASE_URL)
async def seed_tickets():
    with open(Path(__file__).resolve().parent.parent / "data/sample_tickets.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    async with AsyncSession(engine) as session:
        existing = await session.scalar(select(func.count()).select_from(Ticket))
        reference_keys = set((await session.scalars(
            select(ClassificationReference.source_key).where(ClassificationReference.source == "sample_tickets")
        )).all())
        missing = [t for t in tickets if t["id"] not in reference_keys]
        if existing > 0 and not missing:
            print(f"Database already has {existing} tickets and the demo references, skipping seed.")
            return

        for t in tickets:
            if existing > 0 and t["id"] in reference_keys:
                continue
            description = validate_ticket_text(t["text"])
            vector = get_model().encode(description).tolist()

            if t["id"] not in reference_keys:
                session.add(ClassificationReference(
                    text=description, category=t["category"], base_priority=t["priority"],
                    embedding_vector=vector, source="sample_tickets", source_key=t["id"],
                ))
            if existing == 0:
                session.add(Ticket(
                    text=description,
                    category=t["category"],
                    priority=t["priority"],
                    automatic_priority=t["priority"],
                    embedding_vector=vector,
                    embedding_version=1,
                ))

        await session.commit()


async def main():
    try:
        await seed_tickets()
        print("Dane demonstracyjne są gotowe. Skrypt nie tworzy ani nie zmienia schematu.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
