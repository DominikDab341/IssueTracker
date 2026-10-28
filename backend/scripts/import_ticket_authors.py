"""Jawne przypisanie autorów starych rekordów: JSON {id_zgłoszenia: email}."""
import argparse
import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from app.database.database import async_session, engine
from app.models.models import Ticket, User
from app.services.errors import InvalidInputError


async def import_authors(db, mapping):
    if not isinstance(mapping, dict) or not mapping:
        raise InvalidInputError("Podaj niepuste mapowanie identyfikatorów zgłoszeń na adresy e-mail.")
    try:
        entries = sorted((int(key), value.strip().lower()) for key, value in mapping.items())
        if len({key for key, _ in entries}) != len(entries) or any(key <= 0 for key, _ in entries):
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise InvalidInputError("Niepoprawny format mapowania autorów.") from None
    changes = []
    for ticket_id, email in entries:
        ticket = await db.scalar(select(Ticket).where(Ticket.id == ticket_id).with_for_update())
        user = await db.scalar(select(User).where(User.email == email, User.is_approved))
        if ticket is None or ticket.author_id is not None or not ticket.legacy_unowned or user is None:
            raise InvalidInputError("Mapowanie wymaga istniejących zgłoszeń bez autora i zaakceptowanych kont. Nie zmieniono danych.")
        changes.append((ticket, user.id))
    for ticket, user_id in changes:
        ticket.author_id, ticket.legacy_unowned = user_id, False
    await db.commit()
    return len(changes)


async def run(mapping):
    try:
        async with async_session() as db:
            return await import_authors(db, mapping)
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mapping", type=Path)
    args = parser.parse_args()
    try:
        count = asyncio.run(run(json.loads(args.mapping.read_text(encoding="utf-8"))))
    except (InvalidInputError, ValueError, OSError) as exc:
        parser.exit(1, str(exc) + "\n")
    print(f"Przypisano jawnie autorów {count} zgłoszeń.")


if __name__ == "__main__":
    main()
