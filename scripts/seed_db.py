import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

load_dotenv()

from app.settings import settings
from app.database.database import Base
from app.models.models import Ticket

engine = create_engine(settings.sync_database_url)
model = SentenceTransformer(settings.MODEL_NAME)


def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)


def seed_tickets():
    with open("data/sample_tickets.json", "r", encoding="utf-8") as f:
        tickets = json.load(f)

    with Session(engine) as session:
        existing = session.query(Ticket).count()
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

        session.commit()


if __name__ == "__main__":
    init_db()
    seed_tickets()
    print("IssueTracker database is ready. ")
