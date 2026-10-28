"""Jednorazowe utworzenie pierwszego administratora, bez hasła w argumentach."""
import argparse
import asyncio
from getpass import GetPassWarning, getpass
from pathlib import Path
import sys
import warnings

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.database import async_session, engine
from app.services.errors import ConflictError, InvalidInputError
from app.services.users import UserService


async def create(email: str, password: str):
    try:
        async with async_session() as db:
            await UserService(db).bootstrap_admin(email, password)
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="Utwórz pierwszego administratora po wykonaniu migracji.")
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", GetPassWarning)
            password = getpass("Hasło administratora (12–128 znaków): ")
            repeated = getpass("Powtórz hasło: ")
    except (GetPassWarning, EOFError):
        parser.exit(1, "Użyj interaktywnego terminala pozwalającego ukryć hasło. Nie utworzono konta.\n")
    if password != repeated:
        parser.exit(1, "Hasła różnią się. Nie utworzono konta.\n")
    try:
        asyncio.run(create(args.email, password))
    except (ConflictError, InvalidInputError) as exc:
        parser.exit(1, str(exc) + "\n")
    print("Utworzono aktywne i zaakceptowane konto administratora.")


if __name__ == "__main__":
    main()
