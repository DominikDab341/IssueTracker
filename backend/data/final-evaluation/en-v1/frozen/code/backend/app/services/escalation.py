"""Persistent high minimum for a compact group of recent incidents from distinct authors."""
from datetime import timedelta
import math

from sqlalchemy import select

from app.domain import Category
from app.models.models import Ticket
from app.settings import settings
from app.services.priorities import update_effective_priority
from app.services.tasks import now
from app.ticket_status import ACTIVE_STATUSES


def cosine_similarity(left, right):
    if left is None or right is None:
        return -1.0
    norm = math.sqrt(sum(float(x) ** 2 for x in left) * sum(float(x) ** 2 for x in right))
    return sum(float(x) * float(y) for x, y in zip(left, right)) / norm if norm else -1.0


def compact_group(anchor, candidates, threshold):
    """Deterministic clique around the new ticket; never join by a similarity chain."""
    group = [anchor]
    for candidate in sorted(candidates, key=lambda row: row.id):
        if candidate.id == anchor.id:
            continue
        if all(cosine_similarity(candidate.embedding_vector, other.embedding_vector) > threshold for other in group):
            group.append(candidate)
    return group


async def apply_escalation(db, ticket):
    if not settings.ESCALATION_ENABLED or ticket.category not in set(Category):
        return
    timestamp = now()
    cutoff = timestamp - timedelta(hours=settings.ESCALATION_WINDOW_HOURS)
    if (ticket.status not in ACTIVE_STATUSES or ticket.author_id is None or not ticket.classification_current
            or not cutoff <= ticket.created_at <= timestamp):
        return
    await db.flush()
    distance = Ticket.embedding_vector.cosine_distance(ticket.embedding_vector)
    # Same category is deliberately conservative for the automatic business rule.
    matches = list(await db.scalars(select(Ticket).where(
        Ticket.status.in_(ACTIVE_STATUSES), Ticket.author_id.is_not(None),
        Ticket.embedding_version == Ticket.content_version, Ticket.category == ticket.category,
        Ticket.created_at >= cutoff, Ticket.created_at <= timestamp,
        distance < 1 - settings.ESCALATION_MIN_SIMILARITY,
    ).order_by(Ticket.id).with_for_update().execution_options(populate_existing=True)))
    group = compact_group(ticket, matches, settings.ESCALATION_MIN_SIMILARITY)
    authors = {row.author_id for row in group}
    if len(authors) < settings.ESCALATION_MIN_USERS:
        return
    for member in group:
        if member.escalation_min_priority is None:
            member.escalation_min_priority = "high"
            member.escalated_at = timestamp
            member.escalation_reason = (f"Podobne aktywne zgłoszenia od {len(authors)} różnych osób "
                                        f"w oknie {settings.ESCALATION_WINDOW_HOURS:g} godzin.")
            # Internal evidence is never included in the reporter-facing schema.
            member.escalation_evidence = {"ticket_ids": [row.id for row in group], "author_ids": sorted(authors),
                                          "min_similarity": settings.ESCALATION_MIN_SIMILARITY,
                                          "min_users": settings.ESCALATION_MIN_USERS,
                                          "window_hours": settings.ESCALATION_WINDOW_HOURS}
        update_effective_priority(member)
