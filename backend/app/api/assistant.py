from typing import Annotated

import anyio
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_assistant_user
from app.database.database import get_db
from app.models.models import Ticket, User
from app.services.access import require_assistant_access
from app.services.assistant import AnswerPart, AssistantBusyError, ModelUnavailableError, NO_CONTEXT, generate_answer
from app.services.classifier import get_model
from app.services.errors import AuthenticationError, InvalidInputError
from app.services.ticket_search import search_tickets, ticket_scope


router = APIRouter(prefix="/assistant", tags=["assistant"])
Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=600)]


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: Question
    previous_questions: list[Question] = Field(default_factory=list, max_length=2)
    resolved_only: bool = True


class ChatResponse(BaseModel):
    parts: list[AnswerPart] = Field(default_factory=list)
    message: str | None = None


def retrieval_query(question: str, previous_questions: list[str]) -> str:
    model = get_model()
    tokenizer = model.tokenizer
    if len(tokenizer.encode(question, truncation=False)) > model.max_seq_length:
        raise InvalidInputError("The question is too long for ticket search. Shorten it and try again.", field="question")
    # Keep the current question, then include the most recent earlier question that fits.
    query = question
    for previous in reversed(previous_questions):
        candidate = f"{query}\n{previous}"
        if len(tokenizer.encode(candidate, truncation=False)) <= model.max_seq_length:
            query = candidate
    return query


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, actor: User = Depends(get_assistant_user), db: AsyncSession = Depends(get_db)):
    actor_id = actor.id
    query = await anyio.to_thread.run_sync(retrieval_query, body.question, body.previous_questions)
    result = await search_tickets(db, actor, query, resolved_only=body.resolved_only, limit=3)
    if not result.hits:
        return ChatResponse(message=NO_CONTEXT)
    # Release the database connection while the local model generates the reply.
    await db.rollback()
    try:
        answer = await generate_answer(body.question, body.previous_questions, result.hits)
    except AssistantBusyError as exc:
        raise HTTPException(429, "The assistant is answering another question. Try again shortly.") from exc
    except ModelUnavailableError as exc:
        raise HTTPException(503, str(exc)) from exc

    current_actor = await db.get(User, actor_id, populate_existing=True)
    if current_actor is None:
        raise AuthenticationError("Sign in again.")
    require_assistant_access(current_actor)
    if answer.status == "outside_scope":
        return ChatResponse(message="The assistant answers from retrieved tickets. Complete database statistics are outside its scope.")
    if answer.status != "answered":
        return ChatResponse(message=NO_CONTEXT)

    retrieved = {hit.id: (hit.content_version, hit.status, hit.resolution_note) for hit in result.hits}
    cited_ids = {part.ticket_id for part in answer.parts}
    if not cited_ids or not cited_ids.issubset(retrieved):
        return ChatResponse(message=NO_CONTEXT)
    current = await db.execute(
        select(Ticket.id, Ticket.content_version, Ticket.status, Ticket.resolution_note)
        .where(Ticket.id.in_(cited_ids), *ticket_scope(current_actor, body.resolved_only))
    )
    if {row.id: (row.content_version, row.status, row.resolution_note) for row in current} != {
        ticket_id: retrieved[ticket_id] for ticket_id in cited_ids
    }:
        return ChatResponse(message="The source tickets changed while the answer was being generated. Ask again.")
    return ChatResponse(parts=answer.parts)
