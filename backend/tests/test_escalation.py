"""Distinct authors, complete similarity groups and durable escalation precedence."""
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch
import math

from sqlalchemy import select
from tests.test_api import ApiTestCase, setUpModule
from app.domain import Category, ClassificationPrediction, Priority
from app.models.models import Ticket
from app.services.escalation import compact_group
from app.services.tasks import now
from app.settings import settings

VECTOR = [1.0] + [0.0] * 383


class EscalationTests(ApiTestCase):
    async def older(self, author, category="network", status="reported", vector=VECTOR, hours=0, stale=False):
        ident = await self.add_ticket(status=status, category=category, priority="low", embedding=vector,
                                      created_at=now() - timedelta(hours=hours))
        async with self.sessions() as db:
            row = await db.get(Ticket, ident)
            row.author_id = author.id
            row.base_priority = row.automatic_priority = "low"
            if stale:
                row.embedding_version = None
            await db.commit()
        return ident

    async def new(self, author, category="network", vector=VECTOR, priority=Priority.LOW):
        response = await self.client.post("/tickets/", json={"text": "The shared office service is unavailable"}, headers=self.headers(author))
        self.assertEqual(response.status_code, 201)
        row = response.json()["ticket"]
        prediction = ClassificationPrediction(category, priority, priority, vector)
        with patch.object(self.runtime, "classifier", return_value=prediction):
            await self.process(row["current_task_id"])
        return (await self.client.get(f"/tickets/{row['id']}")).json()

    async def test_escalation_updates_all_matching_tickets_in_all_four_categories(self):
        authors = [await self.add_user(f"escalation-{i}@mail.com") for i in range(3)]
        for category in Category:
            first = await self.older(authors[0], category)
            second = await self.older(authors[1], category)
            third = await self.new(authors[2], category)
            for ident in (first, second, third["id"]):
                result = (await self.client.get(f"/tickets/{ident}")).json()
                self.assertEqual(result["priority"], "high")
                self.assertEqual(result["priority_source"], "escalation")
                self.assertEqual(result["base_priority"], "low")
                self.assertEqual(result["escalation_min_priority"], "high")
                self.assertIsNotNone(result["escalated_at"])
                self.assertNotIn("escalation_evidence", result)
                self.assertNotIn("author_ids", result["escalation_reason"])

    async def test_repeated_reports_by_one_author_do_not_reach_three_users(self):
        other = await self.add_user("escalation-other@mail.com")
        await self.older(self.user)
        await self.older(self.user)
        result = await self.new(other)
        self.assertEqual(result["priority"], "low")
        self.assertIsNone(result["escalation_min_priority"])

    async def test_terminal_old_stale_other_category_and_dissimilar_tickets_are_excluded(self):
        authors = [await self.add_user(f"excluded-{i}@mail.com") for i in range(8)]
        await self.older(authors[0])  # Only one eligible older author.
        await self.older(authors[1], status="resolved")
        await self.older(authors[2], status="cancelled")
        await self.older(authors[3], hours=25)
        await self.older(authors[4], stale=True)
        await self.older(authors[5], category="hardware")
        vector = [.84, math.sqrt(1 - .84 ** 2)] + [0.0] * 382
        await self.older(authors[6], vector=vector)
        result = await self.new(authors[7])
        self.assertEqual(result["priority"], "low")

    async def test_no_transitive_join_of_different_incidents(self):
        a = SimpleNamespace(id=1, embedding_vector=[1, 0])
        b = SimpleNamespace(id=2, embedding_vector=[math.sqrt(.5), math.sqrt(.5)])
        c = SimpleNamespace(id=3, embedding_vector=[0, 1])
        self.assertEqual([row.id for row in compact_group(b, [c, a, b], .7)], [2, 1])

    async def test_minimum_survives_window_expiry_and_reclassification_but_manual_decision_wins(self):
        authors = [await self.add_user(f"durable-{i}@mail.com") for i in range(3)]
        await self.older(authors[0])
        await self.older(authors[1])
        third = await self.new(authors[2])
        async with self.sessions() as db:
            rows = list(await db.scalars(select(Ticket)))
            for row in rows:
                if row.id != third["id"]:
                    row.status = "cancelled"
                row.created_at = now() - timedelta(hours=72)
            await db.commit()
        response = await self.client.patch(f"/tickets/{third['id']}", json={"text": "The incident now has a different description"},
                                           headers=self.headers(authors[2]))
        with patch.object(self.runtime, "classifier", return_value=ClassificationPrediction("network", Priority.LOW, Priority.LOW, VECTOR)):
            await self.process(response.json()["task_id"])
        result = (await self.client.get(f"/tickets/{third['id']}")).json()
        self.assertEqual(result["priority"], "high")
        self.assertEqual(result["escalated_at"], third["escalated_at"])
        await self.client.patch(f"/tickets/{third['id']}/priority", json={"priority": "low"}, headers=self.admin_headers)
        changed = await self.client.patch(f"/tickets/{third['id']}", json={"work_blocked": True}, headers=self.headers(authors[2]))
        self.assertEqual(changed.json()["ticket"]["priority"], "low")
        self.assertEqual(changed.json()["ticket"]["priority_source"], "administrator")

    async def test_manual_priority_and_critical_are_preserved_during_group_update(self):
        authors = [await self.add_user(f"precedence-{i}@mail.com") for i in range(3)]
        first = await self.older(authors[0])
        second = await self.older(authors[1])
        await self.client.patch(f"/tickets/{first}/priority", json={"priority": "low"}, headers=self.admin_headers)
        async with self.sessions() as db:
            row = await db.get(Ticket, second)
            row.base_priority = row.automatic_priority = row.priority = "critical"
            await db.commit()
        third = await self.new(authors[2], priority=Priority.CRITICAL)
        self.assertEqual((await self.client.get(f"/tickets/{first}")).json()["priority"], "low")
        self.assertEqual((await self.client.get(f"/tickets/{second}")).json()["priority"], "critical")
        self.assertEqual(third["priority"], "critical")

    async def test_user_count_and_window_are_configurable(self):
        author = await self.add_user("configured-escalation@mail.com")
        await self.older(self.user, hours=2)
        with patch.object(settings, "ESCALATION_MIN_USERS", 2), patch.object(settings, "ESCALATION_WINDOW_HOURS", 1):
            first = await self.new(author)
            self.assertIsNone(first["escalation_min_priority"])
        with patch.object(settings, "ESCALATION_MIN_USERS", 2), patch.object(settings, "ESCALATION_WINDOW_HOURS", 24):
            second = await self.new(author)
            self.assertEqual(second["priority"], "high")

    async def test_failed_result_transaction_rolls_back_group_changes(self):
        from app.services.escalation import apply_escalation
        authors = [await self.add_user(f"rollback-escalation-{i}@mail.com") for i in range(3)]
        first = await self.older(authors[0])
        second = await self.older(authors[1])

        async def fail_after_group_update(db, ticket):
            await apply_escalation(db, ticket)
            raise RuntimeError("controlled failure after group updates")

        with patch("app.services.processing.apply_escalation", side_effect=fail_after_group_update):
            third = await self.new(authors[2])
        self.assertEqual(third["current_task_state"], "failed")
        for ident in (first, second, third["id"]):
            result = (await self.client.get(f"/tickets/{ident}")).json()
            self.assertIsNone(result["escalation_min_priority"])

    async def test_reviewed_priority_fallback_can_be_raised_by_escalation(self):
        authors = [await self.add_user(f"review-escalation-{i}@mail.com") for i in range(3)]
        await self.older(authors[0])
        await self.older(authors[1])
        response = await self.client.post("/tickets/", json={"text": "A shared connectivity issue"}, headers=self.headers(authors[2]))
        ticket = response.json()["ticket"]
        prediction = ClassificationPrediction("network", None, None, VECTOR,
            predicted_base_priority=Priority.LOW, priority_review_reason="low_priority_score")
        with patch.object(self.runtime, "classifier", return_value=prediction):
            await self.process(ticket["current_task_id"])
        result = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertEqual(result["priority"], "high")
        self.assertEqual(result["priority_source"], "escalation")
        self.assertIsNone(result["base_priority"])
        self.assertTrue(result["priority_needs_review"])
