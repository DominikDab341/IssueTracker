import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from app.models.models import Ticket
from app.services.classifier import get_model
from app.services.text_validation import validate_ticket_text

engine = create_async_engine(settings.DATABASE_URL)
async def seed_tickets():
    with open(Path(__file__).resolve().parent.parent / "data/sample_tickets.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    async with AsyncSession(engine) as session:
        existing = await session.scalar(text("SELECT count(*) FROM tickets"))
        if existing > 0:
            print(f"Database already has {existing} tickets, skipping seed.")
            return

        for t in tickets:
            description = validate_ticket_text(t["text"])
            vector = get_model().encode(description).tolist()

            ticket = Ticket(
                text=description,
                category=t["category"],
                priority=t["priority"],
                automatic_priority=t["priority"],
                embedding_vector=vector,
                embedding_version=1,
            )
            session.add(ticket)

        await session.commit()


async def main():
    try:
        await seed_tickets()
        print("Dane demonstracyjne są gotowe. Skrypt nie tworzy ani nie zmienia schematu.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
