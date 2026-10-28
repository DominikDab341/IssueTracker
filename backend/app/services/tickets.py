"""Operacje na zgłoszeniach i granice ich transakcji."""
import anyio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import ACTIVE_TASK_STATES, RETRYABLE_ERRORS, Category, Priority, TaskErrorCode, TaskState
from app.models.models import AssignmentHistory, ClassificationTask, Ticket, User
from app.services.access import Role, available_tickets, require_active, require_roles
from app.services.classifier import find_similar_open_tickets
from app.services.errors import ConflictError, ForbiddenError, InvalidInputError, NotFoundError
from app.services.priorities import update_effective_priority
from app.services.tasks import create_task, fail_task, lock_task, now
from app.services.text_validation import validate_ticket_text
from app.ticket_status import (
    ACTIVE_STATUSES, ALLOWED_TRANSITIONS, TERMINAL_STATUSES, TicketStatus,
    normalize_status_note, validate_status_notes,
)


class TicketService:
    def __init__(self, db: AsyncSession, actor: User):
        self.db = db
        require_active(actor)
        self.actor = actor

    async def _validate_text(self, value: str) -> str:
        try:
            return await anyio.to_thread.run_sync(validate_ticket_text, value)
        except ValueError as exc:
            raise InvalidInputError(str(exc), field="text") from exc

    async def _get(self, ticket_id: int, *, locked: bool = False) -> Ticket:
        query = select(Ticket).where(Ticket.id == ticket_id, available_tickets(self.actor))
        if locked:
            query = query.with_for_update().execution_options(populate_existing=True)
        ticket = await self.db.scalar(query)
        if ticket is None:
            raise NotFoundError("Nie znaleziono zgłoszenia.")
        return ticket

    async def _commit(self, ticket: Ticket) -> None:
        await self.db.commit()
        await self._task_states([ticket])

    async def get(self, ticket_id: int) -> Ticket:
        row = (await self.db.execute(
            self._read_query().where(Ticket.id == ticket_id, available_tickets(self.actor))
        )).first()
        if row is None:
            raise NotFoundError("Nie znaleziono zgłoszenia.")
        ticket, state = row
        ticket.current_task_state = state
        return ticket

    @staticmethod
    def _read_query():
        # One PostgreSQL snapshot: a finished task must not accompany the old ticket result.
        return select(Ticket, ClassificationTask.state).outerjoin(
            ClassificationTask, ClassificationTask.id == Ticket.current_task_id,
        ).execution_options(populate_existing=True)

    async def _task_states(self, tickets: list[Ticket]) -> None:
        if tickets:
            rows = (await self.db.execute(self._read_query().where(Ticket.id.in_([t.id for t in tickets])))).all()
            for ticket, state in rows:
                ticket.current_task_state = state

    async def duplicates(self, ticket_id: int) -> list[dict]:
        ticket = await self._get(ticket_id)
        return await find_similar_open_tickets(
            ticket_id=ticket.id, embedding=ticket.embedding_vector if ticket.classification_current else None,
            category=ticket.category, db=self.db, actor=self.actor,
        )

    async def list_tickets(self, *, status: TicketStatus | None = None, category: str | None = None,
                   priority: str | None = None, needs_review: bool | None = None,
                   limit: int = 20, offset: int = 0) -> list[Ticket]:
        query = self._read_query().where(available_tickets(self.actor)).order_by(Ticket.created_at.desc(), Ticket.id.desc())
        if status is not None:
            query = query.where(Ticket.status == status)
        if category is not None:
            query = query.where(Ticket.category == category)
        if priority is not None:
            query = query.where(Ticket.priority == priority)
        if needs_review is not None:
            require_roles(self.actor, Role.STAFF, Role.ADMIN)
            query = query.where((Ticket.category == "unknown") if needs_review else (Ticket.category != "unknown"))
        result = await self.db.execute(query.limit(limit).offset(offset))
        tickets = []
        for ticket, state in result.all():
            ticket.current_task_state = state
            tickets.append(ticket)
        return tickets

    async def create(self, *, text: str, work_blocked: bool, run_id: str) -> tuple[Ticket, ClassificationTask]:
        text = await self._validate_text(text)
        ticket = Ticket(text=text, category="unknown", priority=Priority.MEDIUM, work_blocked=work_blocked,
                        author_id=self.actor.id)
        update_effective_priority(ticket)
        self.db.add(ticket)
        await self.db.flush()
        task = create_task(ticket, self.db, run_id)
        await self._commit(ticket)
        return ticket, task

    async def get_task(self, ticket_id: int, task_id: str) -> tuple[ClassificationTask, bool]:
        ticket = await self.get(ticket_id)
        task = await self.db.scalar(select(ClassificationTask).where(
            ClassificationTask.id == task_id, ClassificationTask.ticket_id == ticket_id,
        ))
        if task is None:
            raise NotFoundError("Nie znaleziono zadania dla tego zgłoszenia.")
        current = task.id == ticket.current_task_id and task.content_version == ticket.content_version
        return task, current

    async def retry_classification(self, ticket_id: int, *, run_id: str) -> tuple[Ticket, ClassificationTask]:
        ticket = await self._get(ticket_id, locked=True)
        if ticket.status not in ACTIVE_STATUSES:
            raise ConflictError("Nie można ponowić klasyfikacji zakończonego zgłoszenia.")
        if self.actor.role != Role.ADMIN:
            own_report = (ticket.author_id == self.actor.id and ticket.status == TicketStatus.REPORTED
                          and ticket.assignee_id is None)
            assigned = (self.actor.role == Role.STAFF and ticket.assignee_id == self.actor.id
                        and ticket.status in (TicketStatus.ACCEPTED, TicketStatus.IN_PROGRESS))
            if not (own_report or assigned):
                raise ForbiddenError("Brak uprawnień do ponowienia klasyfikacji tego zgłoszenia.")
        previous = await lock_task(self.db, ticket.current_task_id) if ticket.current_task_id else None
        if (previous is None or previous.state != TaskState.FAILED or previous.error_code not in RETRYABLE_ERRORS
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
        if ticket.author_id != self.actor.id:
            raise ForbiddenError("Możesz edytować tylko własne zgłoszenie.")
        if ticket.status != TicketStatus.REPORTED:
            raise ConflictError("Opis i blokadę pracy można edytować tylko w statusie Zgłoszony.")
        task = None
        if text is not None and text != ticket.text:
            previous = await lock_task(self.db, ticket.current_task_id) if ticket.current_task_id else None
            if previous is not None and previous.state in ACTIVE_TASK_STATES:
                fail_task(previous, TaskErrorCode.SUPERSEDED, "Treść zgłoszenia zmieniono; zadanie zastąpiono nową wersją.")
            ticket.text = text
            ticket.content_version += 1
            ticket.category = "unknown"
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
        if status == TicketStatus.CANCELLED:
            if ticket.author_id != self.actor.id or ticket.assignee_id is not None:
                raise ForbiddenError("Możesz anulować tylko własne nieprzypisane zgłoszenie w statusie Zgłoszony.")
        elif status == TicketStatus.ACCEPTED:
            require_roles(self.actor, Role.STAFF)
            if ticket.assignee_id is not None:
                raise ConflictError("Zgłoszenie ma już wykonawcę.")
            await self._assign(ticket, self.actor.id)
        elif status == TicketStatus.REJECTED:
            roles = (Role.STAFF, Role.ADMIN) if ticket.status == TicketStatus.REPORTED else (Role.ADMIN,)
            require_roles(self.actor, *roles)
        elif status in (TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED):
            require_roles(self.actor, Role.STAFF, Role.ADMIN)
            if self.actor.role != Role.ADMIN and ticket.assignee_id != self.actor.id:
                raise ForbiddenError("Operacja wymaga aktualnego przypisania zgłoszenia.")
        ticket.status = status
        ticket.status_changed_by_id, ticket.status_changed_at = self.actor.id, now()
        if status == TicketStatus.RESOLVED:
            ticket.resolution_note = resolution_note
            ticket.resolved_at = now()
            ticket.resolved_by_id = self.actor.id
        if status == TicketStatus.REJECTED:
            ticket.rejection_reason = rejection_reason
            ticket.rejected_at = now()
            ticket.rejected_by_id = self.actor.id
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
            actor=self.actor,
        )
        return ticket, duplicates

    async def _assign(self, ticket: Ticket, assignee_id: int):
        assignee = await self.db.scalar(select(User).where(User.id == assignee_id).with_for_update(read=True)
                                        .execution_options(populate_existing=True))
        if (assignee is None or not assignee.is_active or not assignee.is_approved or assignee.role != Role.STAFF):
            raise InvalidInputError("Wykonawcą może być tylko aktywna, zaakceptowana osoba obsługująca.", field="assignee_id")
        if ticket.assignee_id == assignee_id:
            raise ConflictError("Zgłoszenie jest już przypisane tej osobie.")
        self.db.add(AssignmentHistory(ticket_id=ticket.id, previous_assignee_id=ticket.assignee_id,
                                      assignee_id=assignee_id, changed_by_id=self.actor.id))
        ticket.assignee_id = assignee_id

    async def assign(self, ticket_id: int, assignee_id: int) -> Ticket:
        require_roles(self.actor, Role.ADMIN)
        ticket = await self._get(ticket_id, locked=True)
        if ticket.status not in ACTIVE_STATUSES:
            raise ConflictError("Nie można przypisać zakończonego zgłoszenia.")
        await self._assign(ticket, assignee_id)
        if ticket.status == TicketStatus.REPORTED:
            ticket.status = TicketStatus.ACCEPTED
            ticket.status_changed_by_id, ticket.status_changed_at = self.actor.id, now()
        await self._commit(ticket)
        return ticket

    async def assignment_history(self, ticket_id: int):
        require_roles(self.actor, Role.STAFF, Role.ADMIN)
        await self.get(ticket_id)
        return list((await self.db.scalars(select(AssignmentHistory).where(AssignmentHistory.ticket_id == ticket_id)
                                           .order_by(AssignmentHistory.id))).all())

    async def set_priority(self, ticket_id: int, priority: Priority) -> Ticket:
        require_roles(self.actor, Role.ADMIN)
        ticket = await self._get(ticket_id, locked=True)
        ticket.manual_priority = priority
        ticket.manual_priority_by_id, ticket.manual_priority_at = self.actor.id, now()
        update_effective_priority(ticket)
        await self._commit(ticket)
        return ticket

    async def correct_category(self, ticket_id: int, category: Category, *, expected_content_version: int) -> Ticket:
        require_roles(self.actor, Role.STAFF, Role.ADMIN)
        if type(expected_content_version) is not int or expected_content_version < 1:
            raise InvalidInputError("Podaj dodatnią, całkowitą wersję opisu.", field="expected_content_version")
        try:
            category = Category(category)
        except (ValueError, TypeError):
            raise InvalidInputError("Wybierz kategorię ze słownika.", field="category") from None
        ticket = await self._get(ticket_id, locked=True)
        if self.actor.role != Role.ADMIN and ticket.assignee_id != self.actor.id:
            raise ForbiddenError("Korekta kategorii wymaga aktualnego przypisania zgłoszenia.")
        if ticket.content_version != expected_content_version:
            raise ConflictError("Opis zgłoszenia zmienił się. Odczytaj aktualną treść przed korektą kategorii.")
        ticket.category, ticket.manual_category = category, category
        ticket.manual_category_version = ticket.content_version
        ticket.manual_category_by_id, ticket.manual_category_at = self.actor.id, now()
        await self._commit(ticket)
        return ticket
