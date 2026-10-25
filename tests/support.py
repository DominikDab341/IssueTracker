"""Konfiguracja wyłącznie jawnie wskazanej, oddzielnej bazy testowej."""
import os
from pathlib import Path

from sqlalchemy.engine import make_url

TEST_URL = os.environ.get("TEST_DATABASE_URL")
if not TEST_URL:
    raise RuntimeError("Ustaw TEST_DATABASE_URL na oddzielną bazę issuetracker_test.")
test_url = make_url(TEST_URL)
if test_url.database != "issuetracker_test" or test_url.drivername != "postgresql+asyncpg":
    raise RuntimeError("Testy wymagają PostgreSQL/asyncpg i bazy o nazwie issuetracker_test.")
os.environ["DATABASE_URL"] = TEST_URL

from alembic.config import Config

ROOT = Path(__file__).resolve().parent.parent


def migration_config(mapping=None):
    config = Config(str(ROOT / "app/alembic.ini"))
    if mapping is not None:
        import json
        from argparse import Namespace
        config.cmd_opts = Namespace(x=["legacy_status_map=" + json.dumps(mapping)])
    return config
