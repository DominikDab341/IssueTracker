import asyncio
from collections.abc import Awaitable, Callable
import logging
from traceback import walk_tb
from uuid import uuid4

from sqlalchemy import select, text, update

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain import ACTIVE_TASK_STATES, ClassificationPrediction, TaskErrorCode, TaskState
from app.models.models import ClassificationTask
from app.services.priorities import update_effective_priority
from app.services.tasks import fail_task, lock_task, lock_ticket, now
from app.ticket_status import ACTIVE_STATUSES

logger = logging.getLogger(__name__)
PROCESS_LOCK = 49011202
Classifier = Callable[[str, AsyncSession], Awaitable[ClassificationPrediction]]


def log_task_error(task_id, stage, error):
    # Bez komunikatu wyjątku, parametrów SQL, kodu źródłowego i wartości lokalnych.
    stack = " -> ".join(
        f"{frame.f_code.co_filename}:{line} in {frame.f_code.co_name}"
        for frame, line in walk_tb(error.__traceback__)
    )
    logger.error("Błąd zadania %s: stage=%s error_type=%s traceback=%s",
                 task_id, stage, type(error).__name__, stack)


class ProcessingRuntime:
    """Jeden proces API; BackgroundTasks nie stanowi trwałej kolejki."""

    def __init__(self, sessions: async_sessionmaker[AsyncSession], classifier: Classifier):
        self.sessions = sessions
        self.classifier = classifier
        self.run_id = str(uuid4())
        self.limit = asyncio.Semaphore(1)
        self.connection = None

    async def start(self, engine):
        # Sesyjna blokada pozostaje na dedykowanym połączeniu do końca procesu.
        self.connection = await engine.connect()
        try:
            acquired = await self.connection.scalar(text("SELECT pg_try_advisory_lock(:key)"), {"key": PROCESS_LOCK})
            await self.connection.commit()
            if not acquired:
                raise RuntimeError("Ta baza ma już działający proces API. Wspierany jest jeden proces bez --workers.")
            async with self.sessions() as db:
                await db.execute(update(ClassificationTask).where(
                    ClassificationTask.state.in_(ACTIVE_TASK_STATES),
                ).values(state=TaskState.FAILED, error_code=TaskErrorCode.INTERRUPTED,
                         error="Przetwarzanie przerwano podczas poprzedniego uruchomienia. Możesz je ponowić.",
                         finished_at=now()))
                await db.commit()
        except BaseException:
            await self.stop()
            raise

    async def stop(self):
        if self.connection is not None:
            try:
                await self.connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": PROCESS_LOCK})
                await self.connection.commit()
            finally:
                # Nie oddajemy połączenia z ewentualną blokadą sesyjną do puli.
                await self.connection.invalidate()
                await self.connection.close()
                self.connection = None

    async def _locked(self, db, task_id):
        ticket_id = await db.scalar(select(ClassificationTask.ticket_id).where(ClassificationTask.id == task_id))
        if ticket_id is None:
            return None, None
        # Stała kolejność blokad, również w edycji i ponowieniu: ticket -> task.
        ticket = await lock_ticket(db, ticket_id)
        task = await lock_task(db, task_id)
        return ticket, task

    @staticmethod
    def current(ticket, task):
        return (ticket.current_task_id == task.id and ticket.content_version == task.content_version
                and ticket.status in ACTIVE_STATUSES)

    async def _claim(self, task_id):
        # Utrata połączenia trzymającego blokadę uniemożliwia uruchamianie zadań.
        if self.connection is not None:
            if self.connection.closed or self.connection.invalidated:
                raise RuntimeError("Utracono blokadę procesu API.")
            await self.connection.execute(text("SELECT 1"))
            await self.connection.commit()
        async with self.sessions() as db:
            ticket, task = await self._locked(db, task_id)
            if task is None or task.state != TaskState.PENDING or task.run_id != self.run_id:
                return None
            if not self.current(ticket, task):
                fail_task(task, TaskErrorCode.OBSOLETE, "Zadanie nie dotyczy aktualnej aktywnej wersji zgłoszenia.")
                await db.commit()
                return None
            task.state = TaskState.RUNNING
            task.started_at = now()
            description = ticket.text
            await db.commit()
            return description

    async def _save_result(self, task_id: str, prediction: ClassificationPrediction):
        async with self.sessions() as db:
            ticket, task = await self._locked(db, task_id)
            if task is None or task.state != TaskState.RUNNING or task.run_id != self.run_id:
                return
            if not self.current(ticket, task):
                fail_task(task, TaskErrorCode.OBSOLETE, "Wynik pominięto: zgłoszenie zmieniło treść lub zakończono jego obsługę.")
                await db.commit()
                return
            ticket.predicted_category = prediction.category
            ticket.predicted_category_version = task.content_version
            if not ticket.manual_category_current:
                ticket.category = prediction.category
            ticket.base_priority = prediction.base_priority
            ticket.automatic_priority = prediction.automatic_priority
            ticket.embedding_vector = prediction.vector
            ticket.embedding_version = task.content_version
            update_effective_priority(ticket)
            task.result = {
                "category": prediction.category, "base_priority": ticket.base_priority,
                "automatic_priority": ticket.automatic_priority,
            }
            task.state = TaskState.SUCCEEDED
            task.finished_at = now()
            task.error = None
            task.error_code = None
            # Zapis wyniku i succeeded w tej samej transakcji.
            await db.commit()

    async def _record_failure(self, task_id):
        try:
            async with self.sessions() as db:
                ticket, task = await self._locked(db, task_id)
                if task is not None and task.run_id == self.run_id and task.state in ACTIVE_TASK_STATES:
                    fail_task(task, TaskErrorCode.PROCESSING_FAILED, "Nie udało się sklasyfikować zgłoszenia. Możesz ponowić przetwarzanie.")
                    await db.commit()
        except Exception as exc:
            # Przy całkowitej awarii bazy stan rozpozna następny start API.
            log_task_error(task_id, "record_failure", exc)
            logger.error("Nie zapisano błędu zadania %s; potrzebna kontrola po restarcie.", task_id)

    async def process(self, task_id):
        async with self.limit:
            stage = "claim"
            try:
                description = await self._claim(task_id)
                if description is None:
                    return
                stage = "classify"
                async with self.sessions() as db:
                    prediction = await self.classifier(description, db)
                stage = "save_result"
                await self._save_result(task_id, prediction)
            except asyncio.CancelledError:
                # Pozostawienie pending/running pozwala rozpoznać przerwanie.
                raise
            except Exception as exc:
                # Nie zapisujemy tekstu zgłoszenia ani surowego wyjątku w odpowiedzi.
                log_task_error(task_id, stage, exc)
                await self._record_failure(task_id)
