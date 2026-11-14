from dataclasses import dataclass
from enum import StrEnum
from time import perf_counter

import anyio
from sqlalchemy import func, literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Ticket, User
from app.services.access import available_tickets
from app.services.classifier import encode_text
from app.settings import settings
from app.ticket_status import TicketStatus


class SearchMethod(StrEnum):
    SEMANTIC = "semantic"
    FULL_TEXT = "full_text"


@dataclass(frozen=True)
class SearchHit:
    id: int
    text: str
    status: str
    resolution_note: str | None
    content_version: int
    score: float


@dataclass(frozen=True)
class SearchResult:
    hits: list[SearchHit]
    embedding_ms: float
    search_ms: float


_TEXT_CONFIG = literal_column("'english'::regconfig")
_FULL_TEXT_QUERY = text("""
    to_tsquery('english'::regconfig, nullif(array_to_string(
        ARRAY(SELECT quote_literal(lexeme)
              FROM unnest(tsvector_to_array(to_tsvector('english'::regconfig, :query))) AS lexeme),
        ' | '), ''))
""")


def ticket_scope(actor: User, resolved_only: bool):
    filters = [
        available_tickets(actor),
        Ticket.embedding_vector.is_not(None),
        Ticket.embedding_version == Ticket.content_version,
    ]
    if resolved_only:
        filters.extend([Ticket.status == TicketStatus.RESOLVED, func.btrim(Ticket.resolution_note) != ""])
    return filters


async def search_tickets(db: AsyncSession, actor: User, query: str, *,
                         method: SearchMethod = SearchMethod.SEMANTIC,
                         resolved_only: bool = True, limit: int = 5) -> SearchResult:
    embedding_ms = 0.0
    filters = ticket_scope(actor, resolved_only)
    params = {}
    if method == SearchMethod.SEMANTIC:
        started = perf_counter()
        embedding = await anyio.to_thread.run_sync(encode_text, query)
        embedding_ms = (perf_counter() - started) * 1000
        distance = Ticket.embedding_vector.cosine_distance(embedding)
        score = 1 - distance
        order = distance
        filters.append(distance <= 1 - settings.RAG_MIN_SIMILARITY)
    else:
        document = func.to_tsvector(_TEXT_CONFIG, Ticket.text)
        score = func.ts_rank_cd(document, _FULL_TEXT_QUERY)
        order = score.desc()
        filters.append(document.bool_op("@@")(_FULL_TEXT_QUERY))
        params["query"] = query

    stmt = (
        select(Ticket.id, Ticket.text, Ticket.status, Ticket.resolution_note,
               Ticket.content_version, score.label("score"))
        .where(*filters)
        .order_by(order, Ticket.id)
        .limit(limit)
    )
    started = perf_counter()
    result = await db.execute(stmt, params)
    hits = [SearchHit(**row) for row in result.mappings()]
    return SearchResult(hits, embedding_ms, (perf_counter() - started) * 1000)
