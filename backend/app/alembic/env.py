import sys
from pathlib import Path
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool, text
from alembic import context


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")


from app.database.database import Base
from app.models.models import Ticket  # noqa: F401
from app.settings import settings

config = context.config


database_url = config.attributes.get("database_url", settings.sync_database_url)
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        expected_database = config.attributes.get("expected_database")
        if expected_database is not None:
            actual_database = connection.scalar(text("SELECT current_database()"))
            connection.rollback()  # Zakończ transakcję odczytu przed transakcją Alembic.
            if actual_database != expected_database:
                raise RuntimeError("Migracje testowe odmówiły działania na bazie innej niż issuetracker_test.")
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
