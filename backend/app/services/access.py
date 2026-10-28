"""Wspólna polityka widoczności dla API, duplikatów i przyszłego RAG."""
from enum import StrEnum

from sqlalchemy import true

from app.services.errors import ForbiddenError


class Role(StrEnum):
    REPORTER = "reporter"
    STAFF = "staff"
    ADMIN = "admin"


def require_active(user):
    if not user.is_active or not user.is_approved or user.role not in set(Role):
        raise ForbiddenError("Konto wymaga akceptacji i musi być aktywne.")


def require_roles(user, *roles: Role):
    require_active(user)
    if user.role not in roles:
        raise ForbiddenError("Brak uprawnień do tej operacji.")


def require_assistant_access(user):
    require_roles(user, Role.STAFF, Role.ADMIN)


def available_tickets(user):
    from app.models.models import Ticket
    require_active(user)
    return Ticket.author_id == user.id if user.role == Role.REPORTER else true()
