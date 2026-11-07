"""Legacy category migration keeps original labels and manual decisions."""
import unittest
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from tests.support import TEST_URL, migration_config


class HelpdeskMigrationTests(unittest.TestCase):
    def test_old_manual_category_is_archived_without_changing_business_decisions(self):
        config = migration_config()
        engine = create_engine(make_url(TEST_URL).set(drivername="postgresql+psycopg"))
        try:
            command.upgrade(config, "head")
            with engine.begin() as db:
                db.execute(text("TRUNCATE assignment_history, classification_references, classification_tasks, tickets, users RESTART IDENTITY"))
            command.downgrade(config, "e2b000000001")
            with engine.begin() as db:
                user = db.scalar(text("INSERT INTO users (email,password_hash,role,is_approved,is_active,approved_at) "
                                      "VALUES ('migration@mail.com','unused','admin',true,true,now()) RETURNING id"))
                db.execute(text("INSERT INTO tickets (text,category,priority,status,resolution_note,author_id,"
                                "manual_category,manual_category_version,manual_category_by_id,manual_category_at,"
                                "manual_priority,work_blocked,embedding_version,content_version) "
                                "VALUES ('Legacy issue','bug','low','resolved','Done',:user,'bug',1,:user,now(),"
                                "'low',true,1,1)"), {"user": user})
                before = db.scalar(text("SELECT row_to_json(tickets) FROM tickets"))
            command.upgrade(config, "head")
            with engine.connect() as db:
                after = db.scalar(text("SELECT row_to_json(tickets) FROM tickets"))
            self.assertEqual(after["legacy_category"], "bug")
            self.assertEqual(after["category"], "unknown")
            self.assertIsNone(after["embedding_version"])
            for key in before:
                if key not in ("category", "embedding_version"):
                    self.assertEqual(after[key], before[key], key)
            from app.models.models import Ticket
            self.assertFalse(Ticket(manual_category="bug", manual_category_version=1, content_version=1).manual_category_current)
        finally:
            command.upgrade(config, "head")
            engine.dispose()
