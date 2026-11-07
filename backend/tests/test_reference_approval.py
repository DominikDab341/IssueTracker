"""Approval is explicit, versioned, authorized and independent of operational decisions."""
import asyncio
from unittest.mock import patch

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from tests.test_api import ApiTestCase, setUpModule
from app.models.models import ClassificationReference, Ticket
from app.services.tasks import now

VECTOR = [1.0] + [0.0] * 383


class ReferenceApprovalTests(ApiTestCase):
    async def resolved(self):
        ident = await self.add_ticket(status="resolved", category="software", embedding=VECTOR)
        async with self.sessions() as db:
            ticket = await db.get(Ticket, ident)
            ticket.assignee_id = self.user.id
            ticket.manual_priority, ticket.priority = "critical", "critical"
            ticket.work_blocked = True
            await db.commit()
        return ident

    async def approve(self, ident, actor=None, **overrides):
        body = {"category": "hardware", "base_priority": "low", "expected_content_version": 1, **overrides}
        return await self.client.post(f"/tickets/{ident}/reference", json=body, headers=self.headers(actor or self.user))

    async def test_explicit_labels_audit_no_ticket_mutation_and_duplicate_guard(self):
        ident = await self.resolved()
        before = (await self.client.get(f"/tickets/{ident}")).json()
        first, second = await asyncio.gather(self.approve(ident), self.approve(ident))
        self.assertEqual(sorted([first.status_code, second.status_code]), [201, 409])
        reference = (first if first.status_code == 201 else second).json()
        self.assertEqual(reference["category"], "hardware")
        self.assertEqual(reference["base_priority"], "low")
        self.assertEqual(reference["source_content_version"], 1)
        self.assertEqual(reference["approved_by_id"], self.user.id)
        self.assertIsNotNone(reference["approved_at"])
        self.assertEqual((await self.client.get(f"/tickets/{ident}")).json(), before)
        async with self.sessions() as db:
            row = await db.get(ClassificationReference, reference["id"])
            self.assertEqual(row.source, "approved_ticket")
            self.assertEqual(row.text, before["text"])
            self.assertEqual(list(row.embedding_vector), VECTOR)
            self.assertEqual(await db.scalar(text("SELECT count(*) FROM classification_references")), 1)

    async def test_permissions_current_assignee_admin_and_reporter(self):
        ident = await self.resolved()
        reporter = await self.add_user("reference-reporter@mail.com")
        other = await self.add_user("reference-other@mail.com", "staff")
        for actor in (reporter, other):
            self.assertEqual((await self.approve(ident, actor)).status_code, 403)
        self.assertEqual((await self.client.get(f"/tickets/{ident}/reference", headers=self.headers(reporter))).status_code, 403)
        async with self.sessions() as db:
            ticket = await db.get(Ticket, ident)
            ticket.assignee_id = other.id
            await db.commit()
        self.assertEqual((await self.approve(ident)).status_code, 403)
        self.assertEqual((await self.approve(ident, self.admin)).status_code, 201)

    async def test_unresolved_stale_and_invalid_requests_cannot_approve(self):
        for status in ("reported", "accepted", "in_progress", "rejected", "cancelled"):
            ident = await self.add_ticket(status=status, embedding=VECTOR)
            self.assertEqual((await self.approve(ident, self.admin)).status_code, 409)
        ident = await self.resolved()
        self.assertEqual((await self.approve(ident, expected_content_version=2)).status_code, 409)
        for changes in ({"expected_content_version": True}, {"expected_content_version": 0},
                        {"category": "bug"}, {"base_priority": "urgent"}, {"approved_by_id": self.admin.id}):
            self.assertEqual((await self.approve(ident, **changes)).status_code, 422)
        async with self.sessions() as db:
            ticket = await db.get(Ticket, ident)
            ticket.embedding_version = None
            await db.commit()
        self.assertEqual((await self.approve(ident)).status_code, 409)

    async def test_approved_ticket_becomes_a_reference_and_later_correction_is_independent(self):
        ident = await self.resolved()
        approved = await self.approve(ident)
        self.assertEqual(approved.status_code, 201)
        response = await self.client.post("/tickets/", json={"text": "A completely new printer problem"})
        ticket = response.json()["ticket"]
        with patch("app.services.classifier.encode_text", return_value=VECTOR):
            await self.process(ticket["current_task_id"])
        result = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertEqual(result["category"], "hardware")
        self.assertEqual(result["base_priority"], "low")
        self.assertEqual(result["priority"], "low")
        correction = await self.client.patch(f"/tickets/{ident}/category",
            json={"category": "network", "expected_content_version": 1}, headers=self.admin_headers)
        self.assertEqual(correction.status_code, 200)
        metadata = (await self.client.get(f"/tickets/{ident}/reference")).json()
        self.assertEqual(metadata["category"], "hardware")
        self.assertEqual((await self.approve(ident, category="network")).status_code, 409)

    async def test_new_approval_changes_training_version_and_priority(self):
        await self.add_reference(category="hardware", base_priority="low", embedding=VECTOR)
        ident = await self.resolved()
        async def classify_again():
            response = await self.client.post("/tickets/", json={"text": "Problem z aplikacją."})
            ticket = response.json()["ticket"]
            with patch("app.services.classifier.encode_text", return_value=VECTOR):
                await self.process(ticket["current_task_id"])
            return (await self.client.get(f"/tickets/{ticket['id']}")).json()
        before = await classify_again()
        self.assertEqual(before["base_priority"], "low")
        self.assertEqual((await self.approve(ident, base_priority="high")).status_code, 201)
        after = await classify_again()
        self.assertEqual(after["base_priority"], "high")
        self.assertNotEqual(before["classification_version"], after["classification_version"])

    async def test_database_rejects_an_approval_without_content_version(self):
        ident = await self.resolved()
        async with self.sessions() as db:
            db.add(ClassificationReference(text="Checked incident", category="hardware", base_priority="low",
                embedding_vector=VECTOR, source="approved_ticket", source_key="invalid-approval",
                source_ticket_id=ident, approved_by_id=self.user.id, approved_at=now()))
            with self.assertRaises(IntegrityError):
                await db.commit()
