import unittest

from tests.support import TEST_URL, migration_config
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.database.database import Base
from app.models.models import Ticket  # noqa: F401


class MigrationTests(unittest.TestCase):
    def test_empty_schema_legacy_guard_mapping_and_metadata(self):
        url = make_url(TEST_URL).set(drivername="postgresql+psycopg")
        engine = create_engine(url)
        config = migration_config()
        try:
            command.upgrade(config, "head")
            with engine.begin() as connection:
                connection.execute(text("TRUNCATE classification_references, classification_tasks, tickets"))
            command.downgrade(config, "base")
            command.upgrade(config, "93aaf01f792a")
            with engine.begin() as connection:
                for status in ["open", "resolved", "closed"]:
                    connection.execute(text("INSERT INTO tickets (text,category,priority,status) VALUES ('Stary opis','bug','high',:s)"), {"s": status})
            with self.assertRaisesRegex(RuntimeError, "Istniejące rekordy"):
                command.upgrade(config, "head")
            with engine.connect() as connection:
                self.assertEqual(set(connection.scalars(text("SELECT status FROM tickets"))), {"open", "resolved", "closed"})
                self.assertEqual(connection.scalar(text("SELECT version_num FROM alembic_version")), "93aaf01f792a")
            command.upgrade(migration_config({"open": "reported", "resolved": "resolved", "closed": "cancelled"}), "head")
            with engine.connect() as connection:
                self.assertEqual(set(connection.scalars(text("SELECT status FROM tickets"))), {"reported", "resolved", "cancelled"})
                self.assertEqual(connection.scalar(text("SELECT count(*) FROM tickets WHERE text='Stary opis' AND category='bug' AND priority='high'")), 3)
                self.assertEqual(connection.scalar(text("SELECT count(*) FROM tickets WHERE work_blocked=false AND content_version=1 AND embedding_version IS NULL AND current_task_id IS NULL AND automatic_priority='high' AND base_priority IS NULL AND manual_priority IS NULL AND priority_source='legacy'")), 3)
                self.assertEqual(connection.scalar(text("SELECT count(*) FROM classification_tasks")), 0)
                self.assertEqual(connection.scalar(text("SELECT count(*) FROM classification_references")), 0)
                self.assertEqual(compare_metadata(MigrationContext.configure(connection), Base.metadata), [])
            with self.assertRaisesRegex(RuntimeError, "Cofanie migracji"):
                command.downgrade(config, "93aaf01f792a")
            with engine.connect() as connection:
                self.assertEqual(connection.scalar(text("SELECT version_num FROM alembic_version")), "e5a000000001")
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
