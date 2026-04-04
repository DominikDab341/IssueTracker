import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from app.settings import settings
from app.database.database import Base
from app.models.models import Ticket

engine = create_async_engine(settings.DATABASE_URL)
model = SentenceTransformer(settings.MODEL_NAME)


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)


async def seed_tickets():
    with open("data/sample_tickets.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    async with AsyncSession(engine) as session:
        existing = await session.scalar(text("SELECT count(*) FROM tickets"))
        if existing > 0:
            print(f"Database already has {existing} tickets, skipping seed.")
            return

        for t in tickets:
            vector = model.encode(t["text"]).tolist()

            ticket = Ticket(
                text=t["text"],
                category=t["category"],
                priority=t["priority"],
                embedding_vector=vector,
            )
            session.add(ticket)

        await session.commit()


async def main():
    await init_db()
    await seed_tickets()
    print("IssueTracker database is ready.")


if __name__ == "__main__":
    asyncio.run(main())
