import asyncio
from datetime import datetime, timezone
import logging
from uuid import uuid4

from sqlalchemy import select, text, update

from app.models.models import ClassificationTask, Ticket
from app.services.classifier import classify
from app.services.priorities import PRIORITIES, update_effective_priority
from app.ticket_status import ACTIVE_STATUSES

logger = logging.getLogger(__name__)
PROCESS_LOCK = 49011202
RETRYABLE_ERRORS = {"processing_failed", "interrupted"}


def now():
    return datetime.now(timezone.utc)


def fail_task(task, code, message):
    task.state = "failed"
    task.error_code = code
    task.error = message
    task.finished_at = now()


def create_task(ticket, db, run_id):
    task = ClassificationTask(
        id=str(uuid4()), ticket_id=ticket.id, content_version=ticket.content_version,
        run_id=run_id, state="pending",
    )
    db.add(task)
    ticket.current_task_id = task.id
    return task


async def lock_ticket(db, ticket_id):
    return await db.scalar(select(Ticket).where(Ticket.id == ticket_id).with_for_update().execution_options(populate_existing=True))


async def lock_task(db, task_id):
    return await db.scalar(select(ClassificationTask).where(ClassificationTask.id == task_id).with_for_update().execution_options(populate_existing=True))


class ProcessingRuntime:
    """Jeden proces API; BackgroundTasks nie stanowi trwałej kolejki."""

    def __init__(self, sessions):
        self.sessions = sessions
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
                    ClassificationTask.state.in_(("pending", "running")),
                ).values(state="failed", error_code="interrupted",
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
            if task is None or task.state != "pending" or task.run_id != self.run_id:
                return None
            if not self.current(ticket, task):
                fail_task(task, "obsolete", "Zadanie nie dotyczy aktualnej aktywnej wersji zgłoszenia.")
                await db.commit()
                return None
            task.state = "running"
            task.started_at = now()
            description = ticket.text
            ticket_id = ticket.id
            await db.commit()
            return ticket_id, description

    async def _save_result(self, task_id, prediction):
        async with self.sessions() as db:
            ticket, task = await self._locked(db, task_id)
            if task is None or task.state != "running" or task.run_id != self.run_id:
                return
            if not self.current(ticket, task):
                fail_task(task, "obsolete", "Wynik pominięto: zgłoszenie zmieniło treść lub zakończono jego obsługę.")
                await db.commit()
                return
            ticket.category = prediction["category"]
            ticket.base_priority = prediction.get("base_priority")
            ticket.automatic_priority = prediction["priority"] if prediction["priority"] in PRIORITIES else None
            ticket.embedding_vector = prediction["vector"]
            ticket.embedding_version = task.content_version
            update_effective_priority(ticket)
            task.result = {
                "category": ticket.category, "base_priority": ticket.base_priority,
                "automatic_priority": ticket.automatic_priority,
            }
            task.state = "succeeded"
            task.finished_at = now()
            task.error = None
            task.error_code = None
            # Zapis wyniku i succeeded w tej samej transakcji.
            await db.commit()

    async def _record_failure(self, task_id):
        try:
            async with self.sessions() as db:
                ticket, task = await self._locked(db, task_id)
                if task is not None and task.run_id == self.run_id and task.state in ("pending", "running"):
                    fail_task(task, "processing_failed", "Nie udało się sklasyfikować zgłoszenia. Możesz ponowić przetwarzanie.")
                    await db.commit()
        except Exception:
            # Przy całkowitej awarii bazy stan rozpozna następny start API.
            logger.error("Nie zapisano błędu zadania %s; potrzebna kontrola po restarcie.", task_id)

    async def process(self, task_id):
        async with self.limit:
            try:
                claimed = await self._claim(task_id)
                if claimed is None:
                    return
                ticket_id, description = claimed
                async with self.sessions() as db:
                    prediction = await classify(description, db, ticket_id=ticket_id)
                await self._save_result(task_id, prediction)
            except asyncio.CancelledError:
                # Pozostawienie pending/running pozwala rozpoznać przerwanie.
                raise
            except Exception:
                # Nie zapisujemy tekstu zgłoszenia ani surowego wyjątku w odpowiedzi.
                logger.error("Klasyfikacja zadania %s zakończyła się błędem.", task_id)
                await self._record_failure(task_id)
