"""Ręczny test React na issuetracker_test; nigdy na bazie aplikacji.

Uruchom dopiero po testach unittest (współdzielą tę samą bazę testową).
Encoder jest kontrolowaną atrapą, więc test nie ocenia jakości MiniLM.
"""
import asyncio

from alembic import command
from sqlalchemy import text
import uvicorn

from tests.support import migration_config
from app.api.main import app
from app.database.database import async_session, engine
from app.models.models import ClassificationReference, User
from app.services.auth import password_hasher
from app.services.tasks import now
from app.services import classifier

PASSWORD = "test-password-for-browser"


async def prepare():
    async with engine.begin() as connection:
        await connection.execute(text("TRUNCATE assignment_history, classification_references, classification_tasks, tickets, users RESTART IDENTITY"))
    async with async_session() as db:
        for role in ("reporter", "staff", "admin"):
            db.add(User(email=f"{role}@mail.com", password_hash=password_hasher.hash(PASSWORD),
                        role=role, is_approved=True, is_active=True, approved_at=now()))
        db.add(ClassificationReference(text="Nie działa drukarka.", category="bug", base_priority="medium",
                                       embedding_vector=[1.0] + [0.0] * 383, source="browser-test", source_key="1"))
        await db.commit()
    await engine.dispose()


if __name__ == "__main__":
    command.upgrade(migration_config(), "head")
    asyncio.run(prepare())
    classifier.encode_text = lambda description: [1.0] + [0.0] * 383
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
