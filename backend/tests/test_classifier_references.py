"""KNN korzysta tylko z jawnych przykładów, niezależnie od priorytetów spraw."""
from unittest.mock import patch

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from tests.test_api import ApiTestCase, setUpModule
from app.models.models import ClassificationReference, Ticket
from app.domain import Category


VECTOR = [1.0] + [0.0] * 383


class ClassifierReferenceTests(ApiTestCase):
    async def test_api_uses_new_category_dictionary_and_rejects_old_labels(self):
        ticket = await self.create()
        for category in Category:
            response = await self.client.patch(f"/tickets/{ticket['id']}/category",
                                              json={"category": category, "expected_content_version": 1},
                                              headers=self.admin_headers)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["category"], category)
            self.assertEqual((await self.client.get(f"/tickets/?category={category}")).status_code, 200)
        for old in ("bug", "performance", "feature"):
            self.assertEqual((await self.client.patch(f"/tickets/{ticket['id']}/category",
                json={"category": old, "expected_content_version": 1}, headers=self.admin_headers)).status_code, 422)
            self.assertEqual((await self.client.get(f"/tickets/?category={old}")).status_code, 422)

    async def test_old_reference_source_is_not_used_for_category_or_priority(self):
        ident = await self.add_reference(category="software", base_priority="critical", embedding=VECTOR)
        async with self.sessions() as db:
            reference = await db.get(ClassificationReference, ident)
            reference.source, reference.category = "sample_tickets", "bug"
            await db.commit()
        ticket = await self.classify_new_ticket()
        self.assertEqual(ticket["category"], "unknown")
        self.assertIsNone(ticket["base_priority"])

    async def test_priority_is_learned_from_text_independently_of_nearest_category(self):
        from scripts import seed_db
        from types import SimpleNamespace
        model = SimpleNamespace(encode=lambda value: SimpleNamespace(tolist=lambda: VECTOR))
        with patch.object(seed_db, "engine", self.engine), patch.object(seed_db, "get_model", return_value=model):
            await seed_db.seed_tickets()
        references = seed_db.approved_references()
        critical = next(row for row in references if row["base_priority"] == "critical")
        response = await self.client.post("/tickets/", json={"text": critical["text"]})
        ticket = response.json()["ticket"]
        with patch("app.services.classifier.encode_text", return_value=VECTOR):
            await self.process(ticket["current_task_id"])
        result = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertEqual(result["base_priority"], "critical")
        self.assertTrue(result["classification_version"].startswith("helpdesk-v2:"))
        task = (await self.client.get(f"/tickets/{ticket['id']}/task/{ticket['current_task_id']}")).json()
        self.assertEqual(task["result"]["classification_version"], result["classification_version"])

    async def classify_new_ticket(self, blocked=False):
        response = await self.client.post("/tickets/", json={"text": "Nie działa drukarka.", "work_blocked": blocked})
        self.assertEqual(response.status_code, 201, response.text)
        ticket = response.json()["ticket"]
        with patch("app.services.classifier.encode_text", return_value=VECTOR):
            await self.process(ticket["current_task_id"])
        return (await self.client.get(f"/tickets/{ticket['id']}")).json()

    async def test_checkbox_does_not_propagate_critical_to_following_tickets(self):
        await self.add_reference(category="software", base_priority="low", embedding=VECTOR)
        first = await self.classify_new_ticket(blocked=True)
        self.assertEqual(first["base_priority"], "low")
        self.assertEqual(first["priority"], "critical")
        self.assertEqual(first["priority_source"], "work_blocked")
        for _ in range(4):
            following = await self.classify_new_ticket()
            self.assertEqual(following["category"], "software")
            self.assertEqual(following["base_priority"], "low")
            self.assertEqual(following["priority"], "low")
            self.assertEqual(following["priority_source"], "automatic")
        async with self.sessions() as session:
            self.assertEqual(await session.scalar(text("SELECT count(*) FROM classification_references")), 1)

    async def test_manual_priority_and_closed_tickets_do_not_change_reference(self):
        await self.add_reference(category="software", base_priority="low", embedding=VECTOR)
        first = await self.classify_new_ticket()
        async with self.sessions() as session:
            ticket = await session.get(Ticket, first["id"])
            ticket.manual_priority = "critical"
            ticket.priority = "critical"
            ticket.priority_source = "administrator"
            ticket.status = "cancelled"
            await session.commit()
        following = await self.classify_new_ticket()
        self.assertEqual(following["base_priority"], "low")
        self.assertEqual(following["priority"], "low")

    async def test_operational_tickets_cannot_bootstrap_or_pollute_reference(self):
        for status in ["reported", "accepted", "in_progress", "resolved", "rejected", "cancelled"]:
            await self.add_ticket(status=status, category="software", priority="critical", embedding=VECTOR)
        result = await self.classify_new_ticket()
        self.assertEqual(result["category"], "unknown")
        self.assertIsNone(result["base_priority"])
        self.assertEqual(result["priority"], "medium")
        self.assertEqual(result["priority_source"], "fallback")
        await self.add_reference(category="hardware", base_priority="low", embedding=VECTOR)
        result = await self.classify_new_ticket()
        self.assertEqual(result["category"], "hardware")
        self.assertEqual(result["base_priority"], "low")

    async def test_critical_reference_remains_critical_without_checkbox(self):
        await self.add_reference(category="software", base_priority="critical", embedding=VECTOR)
        result = await self.classify_new_ticket()
        self.assertEqual(result["base_priority"], "critical")
        self.assertEqual(result["priority"], "critical")
        self.assertEqual(result["priority_source"], "automatic")

    async def test_reference_is_independent_of_operational_text_edit(self):
        await self.add_reference(category="software", base_priority="low", embedding=VECTOR)
        first = await self.classify_new_ticket()
        response = await self.client.patch(f"/tickets/{first['id']}", json={"text": "Zupełnie inny problem."})
        self.assertEqual(response.status_code, 200, response.text)
        following = await self.classify_new_ticket()
        self.assertEqual(following["base_priority"], "low")
        async with self.sessions() as session:
            reference = await session.scalar(select(ClassificationReference))
            self.assertEqual(reference.text, "Sprawdzony przykład.")
            self.assertEqual(reference.base_priority, "low")

    async def test_database_rejects_unknown_labels_and_invalid_priorities(self):
        for category, priority in [("unknown", "low"), ("", "low"), ("software", "unknown"), ("software", "urgent")]:
            with self.subTest(category=category, priority=priority):
                with self.assertRaises(IntegrityError):
                    await self.add_reference(category=category, base_priority=priority, embedding=VECTOR)
