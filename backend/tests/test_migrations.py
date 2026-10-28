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
    def test_users_migration_preserves_existing_data_without_inventing_authors(self):
        engine = create_engine(make_url(TEST_URL).set(drivername="postgresql+psycopg"))
        config = migration_config()
        try:
            command.upgrade(config, "head")
            with engine.begin() as connection:
                connection.execute(text("TRUNCATE assignment_history, classification_references, classification_tasks, tickets, users"))
            command.downgrade(config, "e5a000000001")
            with engine.begin() as connection:
                connection.execute(text("""
                    INSERT INTO tickets (text, category, priority, status, resolution_note,
                                         embedding_vector, embedding_version, content_version)
                    VALUES ('Dawny problem', 'bug', 'high', 'resolved', 'Dawne rozwiązanie',
                            CAST(:vector AS vector), 1, 1)
                """), {"vector": str([1.0] + [0.0] * 383)})
                before = connection.scalar(text("SELECT row_to_json(tickets) FROM tickets"))
            command.upgrade(config, "head")
            with engine.connect() as connection:
                after = connection.scalar(text("SELECT row_to_json(tickets) FROM tickets"))
                self.assertEqual({key: after[key] for key in before}, before)
                self.assertTrue(after["legacy_unowned"])
                for key in ["author_id", "assignee_id", "resolved_by_id", "rejected_by_id", "status_changed_by_id"]:
                    self.assertIsNone(after[key])
                self.assertEqual(connection.scalar(text("SELECT count(*) FROM users")), 0)
                self.assertEqual(connection.scalar(text("SELECT count(*) FROM assignment_history")), 0)
        finally:
            engine.dispose()

    def test_empty_schema_legacy_guard_mapping_and_metadata(self):
        url = make_url(TEST_URL).set(drivername="postgresql+psycopg")
        engine = create_engine(url)
        config = migration_config()
        try:
            command.upgrade(config, "head")
            with engine.begin() as connection:
                connection.execute(text("TRUNCATE assignment_history, classification_references, classification_tasks, tickets, users"))
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
                self.assertEqual(connection.scalar(text("SELECT version_num FROM alembic_version")), "e2b000000001")
        finally:
            engine.dispose()

    def test_category_migration_preserves_legacy_data_and_guards_downgrade(self):
        engine = create_engine(make_url(TEST_URL).set(drivername="postgresql+psycopg"))
        config = migration_config()
        try:
            command.upgrade(config, "head")
            with engine.begin() as connection:
                connection.execute(text("TRUNCATE assignment_history, classification_references, classification_tasks, tickets, users"))
            command.downgrade(config, "e3a000000001")
            with engine.begin() as connection:
                connection.execute(text("INSERT INTO tickets (text, category, priority, legacy_unowned) "
                                        "VALUES ('Dawny problem', 'feature', 'high', true)"))
                before = connection.scalar(text("SELECT row_to_json(tickets) FROM tickets"))
            command.upgrade(config, "head")
            with engine.begin() as connection:
                after = connection.scalar(text("SELECT row_to_json(tickets) FROM tickets"))
                self.assertEqual({key: after[key] for key in before}, before)
                self.assertTrue(all(after[key] is None for key in set(after) - set(before)))
                connection.execute(text("UPDATE tickets SET predicted_category='bug', predicted_category_version=1"))
            with self.assertRaisesRegex(RuntimeError, "Cofanie migracji"):
                command.downgrade(config, "e3a000000001")
            with engine.connect() as connection:
                self.assertEqual(connection.scalar(text("SELECT version_num FROM alembic_version")), "e2b000000001")
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
