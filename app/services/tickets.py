"""Operacje na zgłoszeniach i granice ich transakcji."""
import anyio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ACTIVE_TASK_STATES, RETRYABLE_ERRORS, Priority, TaskErrorCode, TaskState
from app.models.models import ClassificationTask, Ticket
from app.services.classifier import find_similar_open_tickets
from app.services.errors import ConflictError, InvalidInputError, NotFoundError
from app.services.priorities import update_effective_priority
from app.services.tasks import create_task, fail_task, lock_task, lock_ticket, now
from app.services.text_validation import validate_ticket_text
from app.ticket_status import (
    ACTIVE_STATUSES, ALLOWED_TRANSITIONS, TERMINAL_STATUSES, TicketStatus,
    normalize_status_note, validate_status_notes,
)


class TicketService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _validate_text(self, value: str) -> str:
        try:
            return await anyio.to_thread.run_sync(validate_ticket_text, value)
        except ValueError as exc:
            raise InvalidInputError(str(exc), field="text") from exc

    async def _get(self, ticket_id: int, *, locked: bool = False) -> Ticket:
        ticket = await lock_ticket(self.db, ticket_id) if locked else await self.db.get(Ticket, ticket_id)
        if ticket is None:
            raise NotFoundError("Nie znaleziono zgłoszenia.")
        return ticket

    async def _commit(self, ticket: Ticket) -> None:
        await self.db.commit()
        await self.db.refresh(ticket)

    async def get(self, ticket_id: int) -> Ticket:
        return await self._get(ticket_id)

    async def list_tickets(self, *, status: TicketStatus | None = None, category: str | None = None,
                   priority: str | None = None, limit: int = 20, offset: int = 0) -> list[Ticket]:
        query = select(Ticket).order_by(Ticket.created_at.desc(), Ticket.id.desc())
        if status is not None:
            query = query.where(Ticket.status == status)
        if category is not None:
            query = query.where(Ticket.category == category)
        if priority is not None:
            query = query.where(Ticket.priority == priority)
        result = await self.db.execute(query.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def create(self, *, text: str, work_blocked: bool, run_id: str) -> tuple[Ticket, ClassificationTask]:
        text = await self._validate_text(text)
        ticket = Ticket(text=text, category="unknown", priority=Priority.MEDIUM, work_blocked=work_blocked)
        update_effective_priority(ticket)
        self.db.add(ticket)
        await self.db.flush()
        task = create_task(ticket, self.db, run_id)
        await self._commit(ticket)
        return ticket, task

    async def get_task(self, ticket_id: int, task_id: str) -> tuple[ClassificationTask, bool]:
        task = await self.db.scalar(select(ClassificationTask).where(
            ClassificationTask.id == task_id, ClassificationTask.ticket_id == ticket_id,
        ))
        if task is None:
            raise NotFoundError("Nie znaleziono zadania dla tego zgłoszenia.")
        ticket = await self.get(ticket_id)
        current = task.id == ticket.current_task_id and task.content_version == ticket.content_version
        return task, current

    async def retry_classification(self, ticket_id: int, *, run_id: str) -> tuple[Ticket, ClassificationTask]:
        ticket = await self._get(ticket_id, locked=True)
        previous = await lock_task(self.db, ticket.current_task_id) if ticket.current_task_id else None
        if (ticket.status not in ACTIVE_STATUSES or previous is None
                or previous.state != TaskState.FAILED or previous.error_code not in RETRYABLE_ERRORS
                or previous.content_version != ticket.content_version):
            raise ConflictError("Można ponowić tylko nieudaną lub przerwaną klasyfikację aktualnego aktywnego zgłoszenia.")
        task = create_task(ticket, self.db, run_id)
        await self._commit(ticket)
        return ticket, task

    async def edit(self, ticket_id: int, *, text: str | None, work_blocked: bool | None,
                   run_id: str) -> tuple[Ticket, ClassificationTask | None]:
        if text is None and work_blocked is None:
            raise InvalidInputError("Podaj opis lub pole blokady pracy.")
        if text is not None:
            text = await self._validate_text(text)
        ticket = await self._get(ticket_id, locked=True)
        if ticket.status != TicketStatus.REPORTED:
            raise ConflictError("Opis i blokadę pracy można edytować tylko w statusie Zgłoszony.")
        task = None
        if text is not None and text != ticket.text:
            previous = await lock_task(self.db, ticket.current_task_id) if ticket.current_task_id else None
            if previous is not None and previous.state in ACTIVE_TASK_STATES:
                fail_task(previous, TaskErrorCode.SUPERSEDED, "Treść zgłoszenia zmieniono; zadanie zastąpiono nową wersją.")
            ticket.text = text
            ticket.content_version += 1
            ticket.base_priority = None
            ticket.automatic_priority = None
            await self.db.flush()
            task = create_task(ticket, self.db, run_id)
        if work_blocked is not None:
            ticket.work_blocked = work_blocked
        update_effective_priority(ticket)
        await self._commit(ticket)
        return ticket, task

    async def change_status(self, ticket_id: int, *, status: TicketStatus,
                            resolution_note: str | None = None, rejection_reason: str | None = None) -> Ticket:
        try:
            resolution_note = normalize_status_note(resolution_note)
            rejection_reason = normalize_status_note(rejection_reason)
            validate_status_notes(status, resolution_note, rejection_reason)
        except ValueError as exc:
            raise InvalidInputError(str(exc)) from exc
        ticket = await self._get(ticket_id, locked=True)
        if status not in ALLOWED_TRANSITIONS.get(ticket.status, set()):
            raise ConflictError("Niedozwolone przejście statusu zgłoszenia.")
        ticket.status = status
        if status == TicketStatus.RESOLVED:
            ticket.resolution_note = resolution_note
            ticket.resolved_at = now()
        if status == TicketStatus.REJECTED:
            ticket.rejection_reason = rejection_reason
            ticket.rejected_at = now()
        await self._commit(ticket)
        return ticket

    async def close(self, ticket_id: int, *, status: TicketStatus,
                    resolution_note: str | None = None, rejection_reason: str | None = None) -> tuple[Ticket, list[dict]]:
        if status not in TERMINAL_STATUSES:
            raise InvalidInputError("Wskaż status końcowy zgłoszenia.")
        ticket = await self.change_status(ticket_id, status=status,
                                          resolution_note=resolution_note, rejection_reason=rejection_reason)
        duplicates = await find_similar_open_tickets(
            ticket_id=ticket.id, embedding=ticket.embedding_vector if ticket.classification_current else None,
            category=ticket.category, db=self.db,
        )
        return ticket, duplicates
