"""Sprawdzenie celu migracji bez łączenia się z PostgreSQL."""
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


ROOT = Path(__file__).resolve().parent.parent


class MigrationIsolationTests(unittest.TestCase):
    def run_probe(self, source):
        environment = os.environ.copy()
        environment["DATABASE_URL"] = "postgresql+asyncpg://probe:unused@127.0.0.1:1/production_probe"
        environment["TEST_DATABASE_URL"] = "postgresql+asyncpg://probe:test%25password@127.0.0.1:1/issuetracker_test"
        result = subprocess.run(
            [sys.executable, "-c", textwrap.dedent(source)], cwd=ROOT,
            env=environment, capture_output=True, text=True, timeout=45,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_explicit_test_url_wins_over_previously_loaded_settings(self):
        self.run_probe('''
            from unittest.mock import patch
            from app.settings import settings
            from sqlalchemy.engine import make_url
            assert make_url(settings.DATABASE_URL).database == "production_probe"
            from tests.support import migration_config
            from alembic import command

            class Inspected(Exception):
                pass

            def inspect_engine(section, **kwargs):
                url = make_url(section["sqlalchemy.url"])
                assert url.database == "issuetracker_test"
                assert url.drivername == "postgresql+psycopg"
                assert url.password == "test%password"
                raise Inspected()

            with patch("sqlalchemy.engine_from_config", side_effect=inspect_engine) as factory:
                try:
                    command.upgrade(migration_config(), "head")
                except Inspected:
                    pass
                else:
                    raise AssertionError("Nie sprawdzono konfiguracji silnika migracji.")
                factory.assert_called_once()
        ''')

    def test_server_database_is_checked_before_migrations(self):
        self.run_probe('''
            from unittest.mock import MagicMock, patch
            from tests.support import migration_config
            from alembic import command

            engine = MagicMock()
            connection = engine.connect.return_value.__enter__.return_value
            connection.scalar.return_value = "production_probe"
            with patch("sqlalchemy.engine_from_config", return_value=engine):
                with patch("alembic.context.configure") as configure:
                    try:
                        command.upgrade(migration_config(), "head")
                    except RuntimeError as exc:
                        assert "Migracje testowe odmówiły" in str(exc)
                    else:
                        raise AssertionError("Migracje nie odmówiły działania na innej bazie.")
                    configure.assert_not_called()
            connection.scalar.assert_called_once()
            connection.rollback.assert_called_once()
        ''')

    def test_cli_without_explicit_url_keeps_settings_database(self):
        self.run_probe('''
            from unittest.mock import patch
            from alembic import command
            from alembic.config import Config
            from sqlalchemy.engine import make_url

            class Inspected(Exception):
                pass

            def inspect_engine(section, **kwargs):
                url = make_url(section["sqlalchemy.url"])
                assert url.database == "production_probe"
                assert url.drivername == "postgresql+psycopg"
                raise Inspected()

            with patch("sqlalchemy.engine_from_config", side_effect=inspect_engine) as factory:
                try:
                    command.upgrade(Config("app/alembic.ini"), "head")
                except Inspected:
                    pass
                else:
                    raise AssertionError("Nie sprawdzono konfiguracji CLI.")
                factory.assert_called_once()
        ''')
