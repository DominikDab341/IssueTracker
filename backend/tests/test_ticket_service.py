from unittest.mock import AsyncMock

from tests.test_api import ApiTestCase, setUpModule
from app.domain import ClassificationPrediction, Priority
from app.models.models import ClassificationTask, Ticket
from app.services.errors import InvalidInputError
from app.services.processing import ProcessingRuntime
from app.services.tickets import TicketService
from app.ticket_status import TicketStatus


VECTOR = [1.0] + [0.0] * 383


class TicketServiceTests(ApiTestCase):
    async def test_service_can_create_ticket_and_task_without_http_or_dispatch(self):
        async with self.sessions() as session:
            ticket, task = await TicketService(session, self.user).create(
                text="  Nie działa drukarka.  ", work_blocked=True, run_id=self.runtime.run_id,
            )
        async with self.sessions() as session:
            stored = await session.get(Ticket, ticket.id)
            stored_task = await session.get(ClassificationTask, task.id)
            self.assertEqual(stored.text, "Nie działa drukarka.")
            self.assertEqual(stored.priority, "critical")
            self.assertEqual(stored.current_task_id, stored_task.id)
            self.assertEqual(stored_task.state, "pending")
        self.mock_delay.assert_not_called()

    async def test_service_enforces_required_notes_without_pydantic_validation(self):
        ticket_id = await self.add_ticket(status="in_progress")
        async with self.sessions() as session:
            with self.assertRaises(InvalidInputError):
                await TicketService(session, self.user).change_status(ticket_id, status=TicketStatus.RESOLVED)
        async with self.sessions() as session:
            ticket = await session.get(Ticket, ticket_id)
            self.assertEqual(ticket.status, "in_progress")
            self.assertIsNone(ticket.resolved_at)

    async def test_each_runtime_uses_its_injected_classifier(self):
        first_classifier = AsyncMock(return_value=ClassificationPrediction("feature", Priority.LOW, Priority.LOW, VECTOR))
        second_classifier = AsyncMock(return_value=ClassificationPrediction("bug", Priority.HIGH, Priority.HIGH, VECTOR))
        first_runtime = ProcessingRuntime(self.sessions, classifier=first_classifier)
        second_runtime = ProcessingRuntime(self.sessions, classifier=second_classifier)
        tickets = []
        for runtime in [first_runtime, second_runtime]:
            async with self.sessions() as session:
                ticket, task = await TicketService(session, self.user).create(
                    text="Nie działa drukarka.", work_blocked=False, run_id=runtime.run_id,
                )
            await runtime.process(task.id)
            tickets.append(ticket.id)
        first_classifier.assert_awaited_once()
        second_classifier.assert_awaited_once()
        async with self.sessions() as session:
            first = await session.get(Ticket, tickets[0])
            second = await session.get(Ticket, tickets[1])
            self.assertEqual((first.category, first.priority), ("feature", "low"))
            self.assertEqual((second.category, second.priority), ("bug", "high"))
