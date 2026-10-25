from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Annotated, Literal

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import async_session, engine, get_db
from app.models.models import ClassificationTask, Ticket
from app.services.classifier import find_similar_open_tickets
from app.services.text_validation import TokenizerUnavailableError, validate_ticket_text
from app.ticket_status import ACTIVE_STATUSES, ALLOWED_TRANSITIONS, TERMINAL_STATUSES, TicketStatus
from app.services.priorities import update_effective_priority
from app.services.processing import ProcessingRuntime, RETRYABLE_ERRORS, create_task, fail_task, lock_task, lock_ticket

class TicketStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: TicketStatus
    resolution_note: str | None = Field(default=None, max_length=2000)
    rejection_reason: str | None = Field(default=None, max_length=2000)

    @field_validator("resolution_note", "rejection_reason")
    @classmethod
    def nonempty_note(cls, value):
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Notatka nie może być pusta.")
        return value

    @model_validator(mode="after")
    def require_notes(self):
        if self.status == TicketStatus.RESOLVED and not self.resolution_note:
            raise ValueError("Rozwiązanie zgłoszenia wymaga opisu rozwiązania.")
        if self.status == TicketStatus.REJECTED and not self.rejection_reason:
            raise ValueError("Odrzucenie zgłoszenia wymaga powodu odrzucenia.")
        if self.resolution_note is not None and self.status != TicketStatus.RESOLVED:
            raise ValueError("Opis rozwiązania można zapisać tylko przy rozwiązaniu zgłoszenia.")
        if self.rejection_reason is not None and self.status != TicketStatus.REJECTED:
            raise ValueError("Powód odrzucenia można zapisać tylko przy odrzuceniu zgłoszenia.")
        return self

class TicketCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str
    work_blocked: StrictBool = False

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return validate_ticket_text(value)


class TicketEdit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str | None = None
    work_blocked: StrictBool | None = None

    @field_validator("text", "work_blocked")
    @classmethod
    def nonnull(cls, value):
        if value is None:
            raise ValueError("Pole nie może mieć wartości null.")
        return value

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        return validate_ticket_text(value)

    @model_validator(mode="after")
    def not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Podaj opis lub pole blokady pracy.")
        return self


class TicketResponse(BaseModel):
    id: int
    text: str
    category: str
    priority: str
    created_at: datetime
    updated_at: datetime
    status: TicketStatus
    resolution_note: str | None
    rejection_reason: str | None
    resolved_at: datetime | None
    rejected_at: datetime | None
    work_blocked: bool
    content_version: int
    embedding_version: int | None
    classification_current: bool
    current_task_id: str | None
    base_priority: str | None
    priority_source: str
    model_config = {"from_attributes": True}


class TicketCreateResponse(BaseModel):
    """Identyfikator zadania zapisanego razem ze zgłoszeniem w PostgreSQL."""
    ticket: TicketResponse
    task_id: str


class TaskStatusResponse(BaseModel):
    task_id: str
    state: Literal["pending", "running", "succeeded", "failed"]
    content_version: int
    current: bool
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    result: dict | None = None
    error: str | None = None
    error_code: str | None = None


class TicketEditResponse(BaseModel):
    ticket: TicketResponse
    task_id: str | None

class SuggestedDuplicate(BaseModel):
    id: int
    text: str
    similarity: float

class TicketCloseResponse(BaseModel):
    ticket: TicketResponse
    status: Literal["resolved", "rejected", "cancelled"]
    suggested_duplicates: list[SuggestedDuplicate] = Field(default_factory=list)

@asynccontextmanager
async def lifespan(app):
    runtime = ProcessingRuntime(async_session)
    await runtime.start(engine)
    app.state.processing_runtime = runtime
    try:
        yield
    finally:
        await runtime.stop()
        await engine.dispose()


app = FastAPI(lifespan=lifespan)


def get_processing_runtime(request: Request):
    runtime = getattr(request.app.state, "processing_runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="Przetwarzanie nie jest gotowe.")
    return runtime


@app.exception_handler(TokenizerUnavailableError)
async def tokenizer_error_handler(request: Request, exc: TokenizerUnavailableError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        context = error.get("ctx", {})
        message = str(context["error"]) if "error" in context else "Niepoprawna lub brakująca wartość."
        errors.append({"loc": list(error["loc"]), "type": error["type"], "msg": message})
    return JSONResponse(status_code=422, content={"detail": errors})


@app.get("/tickets/", response_model=list[TicketResponse])
async def get_tickets(
    status: TicketStatus | None = None,
    category: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    priority: Literal["low", "medium", "high", "critical", "unknown"] | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(Ticket).order_by(Ticket.created_at.desc(), Ticket.id.desc())
    if status is not None:
        query = query.where(Ticket.status == status)
    if category is not None:
        query = query.where(Ticket.category == category)
    if priority is not None:
        query = query.where(Ticket.priority == priority)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    tickets = result.scalars().all()
    return tickets


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    ticket = await db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono zgłoszenia.")
    return ticket


@app.post("/tickets/", response_model=TicketCreateResponse, status_code=201)
async def create_ticket(body: TicketCreate, background_tasks: BackgroundTasks,
                        db: AsyncSession = Depends(get_db), runtime: ProcessingRuntime = Depends(get_processing_runtime)):
    ticket = Ticket(
        text=body.text,
        category="unknown",
        priority="medium",
        work_blocked=body.work_blocked,
    )
    update_effective_priority(ticket)
    db.add(ticket)
    await db.flush()
    task = create_task(ticket, db, runtime.run_id)
    await db.commit()
    await db.refresh(ticket)

    background_tasks.add_task(runtime.process, task.id)

    return TicketCreateResponse(ticket=ticket, task_id=task.id)


@app.get("/tickets/{ticket_id}/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(ticket_id: int, task_id: str, db: AsyncSession = Depends(get_db)):
    task = await db.scalar(select(ClassificationTask).where(ClassificationTask.id == task_id, ClassificationTask.ticket_id == ticket_id))
    if task is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono zadania dla tego zgłoszenia.")
    ticket = await db.get(Ticket, ticket_id)
    return TaskStatusResponse(
        task_id=task.id, state=task.state, content_version=task.content_version,
        current=task.id == ticket.current_task_id and task.content_version == ticket.content_version,
        created_at=task.created_at, started_at=task.started_at, finished_at=task.finished_at,
        result=task.result, error=task.error, error_code=task.error_code,
    )


@app.post("/tickets/{ticket_id}/classification/retry", response_model=TicketCreateResponse, status_code=202)
async def retry_classification(ticket_id: int, background_tasks: BackgroundTasks,
                               db: AsyncSession = Depends(get_db), runtime: ProcessingRuntime = Depends(get_processing_runtime)):
    ticket = await lock_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono zgłoszenia.")
    previous = await lock_task(db, ticket.current_task_id) if ticket.current_task_id else None
    if (ticket.status not in ACTIVE_STATUSES or previous is None
            or previous.state != "failed" or previous.error_code not in RETRYABLE_ERRORS
            or previous.content_version != ticket.content_version):
        raise HTTPException(status_code=409, detail="Można ponowić tylko nieudaną lub przerwaną klasyfikację aktualnego aktywnego zgłoszenia.")
    task = create_task(ticket, db, runtime.run_id)
    await db.commit()
    await db.refresh(ticket)
    background_tasks.add_task(runtime.process, task.id)
    return TicketCreateResponse(ticket=ticket, task_id=task.id)


@app.patch("/tickets/{ticket_id}", response_model=TicketEditResponse)
async def edit_ticket(ticket_id: int, body: TicketEdit, background_tasks: BackgroundTasks,
                      db: AsyncSession = Depends(get_db), runtime: ProcessingRuntime = Depends(get_processing_runtime)):
    ticket = await lock_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono zgłoszenia.")
    if ticket.status != TicketStatus.REPORTED:
        raise HTTPException(status_code=409, detail="Opis i blokadę pracy można edytować tylko w statusie Zgłoszony.")
    description_changed = body.text is not None and body.text != ticket.text
    if description_changed:
        previous = await lock_task(db, ticket.current_task_id) if ticket.current_task_id else None
        if previous is not None and previous.state in ("pending", "running"):
            fail_task(previous, "superseded", "Treść zgłoszenia zmieniono; zadanie zastąpiono nową wersją.")
        ticket.text = body.text
        ticket.content_version += 1
        ticket.base_priority = None
        ticket.automatic_priority = None
        await db.flush()
        task = create_task(ticket, db, runtime.run_id)
    if body.work_blocked is not None:
        ticket.work_blocked = body.work_blocked
    update_effective_priority(ticket)
    await db.commit()
    await db.refresh(ticket)
    if description_changed:
        background_tasks.add_task(runtime.process, task.id)
    return TicketEditResponse(ticket=ticket, task_id=ticket.current_task_id)


async def change_ticket_status(ticket_id: int, body: TicketStatusUpdate, db: AsyncSession):
    # Blokada obejmuje odczyt i zapis, więc równoległa operacja nie omija macierzy.
    ticket = await db.scalar(select(Ticket).where(Ticket.id == ticket_id).with_for_update())
    if ticket is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono zgłoszenia.")
    if body.status not in ALLOWED_TRANSITIONS.get(ticket.status, set()):
        raise HTTPException(status_code=409, detail="Niedozwolone przejście statusu zgłoszenia.")
    ticket.status = body.status
    if body.status == TicketStatus.RESOLVED:
        ticket.resolution_note = body.resolution_note
        ticket.resolved_at = datetime.now(timezone.utc)
    if body.status == TicketStatus.REJECTED:
        ticket.rejection_reason = body.rejection_reason
        ticket.rejected_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ticket)

    return ticket


@app.patch("/tickets/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(ticket_id: int, body: TicketStatusUpdate, db: AsyncSession = Depends(get_db)):
    return await change_ticket_status(ticket_id, body, db)


@app.delete("/tickets/{ticket_id}", response_model=TicketCloseResponse, deprecated=True)
async def delete_ticket(ticket_id: int, body: TicketStatusUpdate, db: AsyncSession = Depends(get_db)):
    """Zgodność ze starym adresem: jawny status końcowy, bez usuwania rekordu."""
    if body.status not in TERMINAL_STATUSES:
        raise HTTPException(status_code=422, detail="Wskaż status końcowy zgłoszenia.")
    ticket = await change_ticket_status(ticket_id, body, db)

    duplicates = await find_similar_open_tickets(
        ticket_id=ticket.id,
        embedding=ticket.embedding_vector if ticket.classification_current else None,
        category=ticket.category,
        db=db,
    )


    return TicketCloseResponse(
        ticket=ticket,
        status=ticket.status,
        suggested_duplicates=duplicates,
    )

