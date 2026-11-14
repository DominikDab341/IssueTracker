"""Resolved tickets join the operational reference set in the status transaction."""
import asyncio
from unittest.mock import patch

from sqlalchemy import select
from tests.test_api import ApiTestCase, setUpModule
from app.models.models import ClassificationReference, Ticket

VECTOR = [1.0] + [0.0] * 383
DESCRIPTION = "The printer cover is scratched. I can work normally."


class ResolvedReferenceTests(ApiTestCase):
    async def in_progress(self, *, vector=VECTOR, category="hardware", base_priority="low"):
        ident = await self.add_ticket(status="in_progress", category=category, embedding=vector)
        async with self.sessions.begin() as db:
            ticket = await db.get(Ticket, ident)
            ticket.text = DESCRIPTION
            ticket.base_priority = base_priority
            ticket.priority = "critical"
            ticket.work_blocked = True
        return ident

    async def resolve(self, ident, actor=None):
        return await self.client.patch(
            f"/tickets/{ident}/status",
            json={"status": "resolved", "resolution_note": "Replaced the cover."},
            headers=self.headers(actor or self.user),
        )

    async def test_resolution_creates_one_audited_reference_from_base_labels(self):
        ident = await self.in_progress()
        other = await self.add_user("other@mail.com", "staff")
        self.assertEqual((await self.resolve(ident, other)).status_code, 403)
        self.assertIsNone((await self.client.get(f"/tickets/{ident}/reference")).json())

        results = await asyncio.gather(self.resolve(ident), self.resolve(ident))
        self.assertEqual(sorted(response.status_code for response in results), [200, 409])
        metadata = (await self.client.get(f"/tickets/{ident}/reference")).json()
        self.assertEqual(metadata["approved_by_id"], self.user.id)
        self.assertEqual(metadata["source_content_version"], 1)
        async with self.sessions() as db:
            references = (await db.scalars(select(ClassificationReference))).all()
            self.assertEqual(len(references), 1)
            self.assertEqual(references[0].source, "resolved_ticket")
            self.assertEqual(references[0].category, "hardware")
            self.assertEqual(references[0].base_priority, "low")
            self.assertEqual(references[0].text, DESCRIPTION)
            self.assertEqual(list(references[0].embedding_vector), VECTOR)
            self.assertEqual((await db.get(Ticket, ident)).priority, "critical")

        created = await self.client.post("/tickets/", json={"text": DESCRIPTION})
        ticket = created.json()["ticket"]
        with patch("app.services.classifier.encode_text", return_value=VECTOR):
            await self.process(ticket["current_task_id"])
        result = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertEqual(result["category"], "hardware")
        self.assertEqual(result["base_priority"], "low")

    async def test_missing_base_priority_or_embedding_does_not_block_resolution(self):
        for options in ({"base_priority": None}, {"vector": None}):
            ident = await self.in_progress(**options)
            self.assertEqual((await self.resolve(ident)).status_code, 200)
            self.assertIsNone((await self.client.get(f"/tickets/{ident}/reference")).json())

    async def test_valid_category_correction_can_complete_a_resolved_reference(self):
        ident = await self.in_progress(category="unknown")
        self.assertEqual((await self.resolve(ident, self.admin)).status_code, 200)
        self.assertIsNone((await self.client.get(f"/tickets/{ident}/reference")).json())
        for category in ("hardware", "network"):
            correction = await self.client.patch(f"/tickets/{ident}/category",
                json={"category": category, "expected_content_version": 1}, headers=self.admin_headers)
            self.assertEqual(correction.status_code, 200)
        metadata = (await self.client.get(f"/tickets/{ident}/reference")).json()
        self.assertEqual(metadata["category"], "hardware")
        self.assertEqual(metadata["approved_by_id"], self.admin.id)
