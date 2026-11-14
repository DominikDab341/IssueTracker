"""Full endpoint and real MiniLM/TF-IDF against the isolated test database."""
from unittest.mock import patch
from sqlalchemy import text
from tests.test_api import ApiTestCase, setUpModule
from scripts import seed_db


class HelpdeskRuntimeTests(ApiTestCase):
    async def test_new_english_ticket_runs_real_models_without_becoming_a_reference(self):
        with patch.object(seed_db, "engine", self.engine):
            await seed_db.seed_tickets()
        description = ("The office wireless connection keeps disconnecting during calls. "
                       "Our team can continue working using Ethernet cables.")
        self.assertNotIn(description, [row["text"] for row in seed_db.approved_references()])
        response = await self.client.post("/tickets/", json={"text": description, "work_blocked": True})
        self.assertEqual(response.status_code, 201, response.text)
        ticket = response.json()["ticket"]
        await self.process(ticket["current_task_id"])
        result = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertEqual(result["current_task_state"], "succeeded")
        self.assertEqual(result["category"], "network")
        self.assertIn(result["base_priority"], ("low", "medium", "high", "critical"))
        self.assertEqual(result["priority"], "critical")
        self.assertEqual(result["priority_source"], "work_blocked")
        self.assertTrue(result["classification_version"].startswith("helpdesk-v2:"))
        async with self.sessions() as db:
            self.assertEqual(await db.scalar(text("SELECT count(*) FROM classification_references")), 120)
            self.assertEqual(await db.scalar(text("SELECT count(*) FROM tickets")), 1)

    async def test_legacy_reclassification_preserves_manual_priority_and_status(self):
        from app.domain import ClassificationPrediction, Priority
        from app.models.models import Ticket
        ident = await self.add_ticket(status="resolved", category="unknown")
        async with self.sessions() as db:
            ticket = await db.get(Ticket, ident)
            ticket.legacy_category = "feature"
            ticket.manual_priority, ticket.priority = "low", "low"
            ticket.work_blocked = True
            await db.commit()
        prediction = ClassificationPrediction("software", Priority.HIGH, Priority.HIGH, [1.0] + [0.0] * 383,
                                               "test-helpdesk-version")
        with patch.object(seed_db, "engine", self.engine), patch.object(seed_db, "classify", return_value=prediction):
            await seed_db.reclassify_legacy()
        result = (await self.client.get(f"/tickets/{ident}")).json()
        self.assertEqual(result["category"], "software")
        self.assertEqual(result["legacy_category"], "feature")
        self.assertEqual(result["priority"], "low")
        self.assertEqual(result["priority_source"], "administrator")
        self.assertEqual(result["status"], "resolved")
