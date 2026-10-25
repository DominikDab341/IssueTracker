"""Zapis zadań i wspólne blokady, używane przez API i wykonawcę zadań."""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import TaskErrorCode, TaskState
from app.models.models import ClassificationTask, Ticket


def now() -> datetime:
    return datetime.now(timezone.utc)


def fail_task(task: ClassificationTask, code: TaskErrorCode, message: str) -> None:
    task.state = TaskState.FAILED
    task.error_code = code
    task.error = message
    task.finished_at = now()


def create_task(ticket: Ticket, db: AsyncSession, run_id: str) -> ClassificationTask:
    task = ClassificationTask(
        id=str(uuid4()), ticket_id=ticket.id, content_version=ticket.content_version,
        run_id=run_id, state=TaskState.PENDING,
    )
    db.add(task)
    ticket.current_task_id = task.id
    return task


async def lock_ticket(db: AsyncSession, ticket_id: int) -> Ticket | None:
    return await db.scalar(select(Ticket).where(Ticket.id == ticket_id)
                           .with_for_update().execution_options(populate_existing=True))


async def lock_task(db: AsyncSession, task_id: str) -> ClassificationTask | None:
    return await db.scalar(select(ClassificationTask).where(ClassificationTask.id == task_id)
                           .with_for_update().execution_options(populate_existing=True))
