"""Rejected predictions remain observable without bypassing manual decisions or workflow."""
from unittest.mock import patch

from tests.test_api import ApiTestCase, setUpModule
from app.domain import ClassificationPrediction, Priority
from app.services.priority_classifier import PriorityPrediction

VECTOR = [1.0] + [0.0] * 383


class DecisionReviewTests(ApiTestCase):
    async def test_split_category_vote_preserves_raw_candidate(self):
        for category in ("hardware", "network", "software"):
            await self.add_reference(category=category, embedding=VECTOR)
        ticket = await self.create()
        with patch("app.services.classifier.encode_text", return_value=VECTOR):
            await self.process(ticket["current_task_id"])
        result = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertEqual(result["category"], "unknown")
        self.assertEqual(result["predicted_category"], "hardware")
        self.assertEqual(result["category_review_reason"], "split_category_vote")
        self.assertEqual(result["current_task_state"], "succeeded")

    async def test_priority_only_review_uses_fallback_and_is_in_review_filter(self):
        await self.add_reference(category="software", embedding=VECTOR)
        ticket = await self.create()
        low_score = PriorityPrediction(Priority.CRITICAL, .30, "review-version", True)
        with patch("app.services.classifier.encode_text", return_value=VECTOR), \
                patch("app.services.classifier.predict_priority_details", return_value=low_score):
            await self.process(ticket["current_task_id"])
        result = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertEqual(result["category"], "software")
        self.assertIsNone(result["base_priority"])
        self.assertEqual(result["predicted_base_priority"], "critical")
        self.assertEqual(result["priority"], "medium")
        self.assertEqual(result["priority_source"], "fallback")
        self.assertTrue(result["needs_review"])
        self.assertEqual([row["id"] for row in (await self.client.get("/tickets/?needs_review=true")).json()], [ticket["id"]])
        self.assertEqual((await self.client.get("/tickets/?needs_review=false")).json(), [])

    async def test_review_fallback_keeps_checkbox_and_manual_priority(self):
        for manual in (None, "low"):
            response = await self.client.post("/tickets/", json={"text": "An ambiguous incident", "work_blocked": True})
            ticket = response.json()["ticket"]
            if manual:
                await self.client.patch(f"/tickets/{ticket['id']}/priority", json={"priority": manual}, headers=self.admin_headers)
            prediction = ClassificationPrediction("unknown", None, None, VECTOR,
                predicted_category="software", predicted_base_priority=Priority.HIGH,
                category_review_reason="low_category_similarity", priority_review_reason="low_priority_score")
            with patch.object(self.runtime, "classifier", return_value=prediction):
                await self.process(ticket["current_task_id"])
            result = (await self.client.get(f"/tickets/{ticket['id']}")).json()
            self.assertEqual(result["priority"], manual or "critical")
            self.assertTrue(result["priority_needs_review"])
            self.assertEqual(result["status"], "reported")
            self.assertEqual(result["current_task_state"], "succeeded")

    async def test_edit_invalidates_old_review_flags_until_current_result(self):
        ticket = await self.create()
        prediction = ClassificationPrediction("software", None, None, VECTOR, priority_review_reason="low_priority_score")
        with patch.object(self.runtime, "classifier", return_value=prediction):
            await self.process(ticket["current_task_id"])
        response = await self.client.patch(f"/tickets/{ticket['id']}", json={"text": "A different detailed incident"})
        self.assertFalse(response.json()["ticket"]["priority_needs_review"])
        self.assertEqual(response.json()["ticket"]["review_version"], 1)
