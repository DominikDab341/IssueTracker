import asyncio
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from app.models.models import ClassificationReference, Ticket, User
from app.services.classifier import get_model
from app.services.text_validation import validate_ticket_text

engine = create_async_engine(settings.DATABASE_URL)
async def seed_tickets(author_email: str | None = None):
    with open(Path(__file__).resolve().parent.parent / "data/sample_tickets.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    async with AsyncSession(engine) as session:
        author = None
        if author_email:
            author = await session.scalar(select(User).where(User.email == author_email.strip().lower(), User.is_approved))
            if author is None:
                raise ValueError("Wskaż istniejące, zaakceptowane konto autora danych demonstracyjnych.")
        existing = await session.scalar(select(func.count()).select_from(Ticket))
        reference_keys = set((await session.scalars(
            select(ClassificationReference.source_key).where(ClassificationReference.source == "sample_tickets")
        )).all())
        missing = [t for t in tickets if t["id"] not in reference_keys]
        create_demo = existing == 0 and author is not None
        if not create_demo and not missing:
            print(f"Database already has {existing} tickets and the demo references, skipping seed.")
            return

        for t in tickets:
            if not create_demo and t["id"] in reference_keys:
                continue
            description = validate_ticket_text(t["text"])
            vector = get_model().encode(description).tolist()

            if t["id"] not in reference_keys:
                session.add(ClassificationReference(
                    text=description, category=t["category"], base_priority=t["priority"],
                    embedding_vector=vector, source="sample_tickets", source_key=t["id"],
                ))
            if create_demo:
                session.add(Ticket(
                    author_id=author.id,
                    text=description,
                    category=t["category"],
                    priority=t["priority"],
                    automatic_priority=t["priority"],
                    embedding_vector=vector,
                    embedding_version=1,
                ))

        await session.commit()


async def main():
    parser = argparse.ArgumentParser(description="Uzupełnij referencje; opcjonalnie dodaj zgłoszenia demonstracyjne z jawnym autorem.")
    parser.add_argument("--author-email")
    args = parser.parse_args()
    try:
        await seed_tickets(args.author_email)
        print("Dane demonstracyjne są gotowe. Skrypt nie tworzy ani nie zmienia schematu.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
