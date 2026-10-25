import asyncio
from dataclasses import replace
from unittest.mock import patch

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from tests.test_api import ApiTestCase, setUpModule
from app.domain import ClassificationPrediction, Priority
from app.models.models import Ticket
from app.services.errors import InvalidInputError
from app.services.tickets import TicketService

VECTOR = [1.0] + [0.0] * 383
PREDICTION = ClassificationPrediction("bug", Priority.HIGH, Priority.HIGH, VECTOR)


class CategoryCorrectionTests(ApiTestCase):
    async def correct(self, ticket, category="feature", actor=None):
        return await self.client.patch(f"/tickets/{ticket['id']}/category",
                                        json={"category": category, "expected_content_version": ticket["content_version"]},
                                        headers=self.headers(actor or self.admin))

    async def detail(self, ticket):
        response = await self.client.get(f"/tickets/{ticket['id']}")
        self.assertEqual(response.status_code, 200)
        return response.json()

    async def run_classification(self, task_id, prediction=PREDICTION):
        with patch.object(self.runtime, "classifier", return_value=prediction):
            await self.process(task_id)

    async def test_category_dictionary_validation_and_no_metadata_spoofing(self):
        ticket = await self.create()
        path = f"/tickets/{ticket['id']}/category"
        for body in [{}, {"category": None}, {"category": ""}, {"category": "unknown"}, {"category": "other"},
                     {"category": " bug "}, {"category": 1}, {"category": "bug", "manual_category_by_id": self.user.id},
                     {"category": "bug", "content_version": 99}]:
            payload = {"expected_content_version": ticket["content_version"], **body}
            self.assertEqual((await self.client.patch(path, json=payload, headers=self.admin_headers)).status_code, 422, str(body))
        self.assertEqual((await self.client.patch(path, json={"category": "bug"}, headers=self.admin_headers)).status_code, 422)
        for version in [None, 0, -1, True, "1", 1.0]:
            payload = {"category": "bug", "expected_content_version": version}
            self.assertEqual((await self.client.patch(path, json=payload, headers=self.admin_headers)).status_code, 422, str(version))
        self.assertEqual((await self.client.patch("/tickets/999999/category", json={"category": "bug", "expected_content_version": 1}, headers=self.admin_headers)).status_code, 404)
        async with self.sessions() as db:
            with self.assertRaises(InvalidInputError):
                await TicketService(db, self.admin).correct_category(ticket["id"], "other", expected_content_version=1)
            for version in [None, 0, -1, True, "1", 1.0]:
                with self.assertRaises(InvalidInputError):
                    await TicketService(db, self.admin).correct_category(ticket["id"], "bug", expected_content_version=version)
        self.assertIsNone((await self.detail(ticket))["manual_category"])

    async def test_stale_view_cannot_correct_new_text_before_or_after_classification(self):
        for classify_first in (False, True):
            with self.subTest(classify_first=classify_first):
                old_view = await self.create()
                edit = await self.client.patch(f"/tickets/{old_view['id']}", json={"text": "Potrzebuję nowej funkcji eksportu do CSV."})
                self.assertEqual(edit.status_code, 200)
                task_id = edit.json()["task_id"]
                prediction = replace(PREDICTION, category="feature")
                if classify_first:
                    await self.run_classification(task_id, prediction)
                before = await self.detail(old_view)
                stale = await self.correct(old_view, "performance")
                self.assertEqual(stale.status_code, 409, stale.text)
                self.assertEqual(await self.detail(old_view), before)
                if not classify_first:
                    await self.run_classification(task_id, prediction)
                current = await self.detail(old_view)
                self.assertEqual(current["content_version"], 2)
                self.assertEqual(current["category"], "feature")
                self.assertEqual(current["predicted_category"], "feature")
                self.assertIsNone(current["manual_category"])
                self.assertFalse(current["manual_category_current"])
                valid = await self.correct(current, "performance")
                self.assertEqual(valid.status_code, 200, valid.text)
                self.assertEqual(valid.json()["manual_category_version"], 2)
                self.assertEqual(valid.json()["category"], "performance")

    async def test_version_is_checked_after_waiting_for_concurrent_edit_lock(self):
        old_view = await self.create()
        editing, release, correcting = asyncio.Event(), asyncio.Event(), asyncio.Event()
        original_commit, original_get = TicketService._commit, TicketService._get

        async def commit(service, ticket):
            if service.actor.id == self.user.id:
                editing.set()
                await release.wait()
            await original_commit(service, ticket)

        async def get(service, ticket_id, *, locked=False):
            if locked and service.actor.id == self.admin.id:
                correcting.set()
            return await original_get(service, ticket_id, locked=locked)

        with patch.object(TicketService, "_commit", commit), patch.object(TicketService, "_get", get):
            edit = asyncio.create_task(self.client.patch(f"/tickets/{old_view['id']}", json={"text": "Nowy opis awarii."}))
            correction = None
            try:
                await asyncio.wait_for(editing.wait(), 5)
                correction = asyncio.create_task(self.correct(old_view))
                await asyncio.wait_for(correcting.wait(), 5)
                self.assertFalse(correction.done())
            finally:
                release.set()
                edit_response = await edit
                if correction is not None:
                    correction_response = await correction
        self.assertEqual(edit_response.status_code, 200)
        self.assertEqual(correction_response.status_code, 409, correction_response.text)
        current = await self.detail(old_view)
        self.assertEqual(current["content_version"], 2)
        self.assertIsNone(current["manual_category"])
        self.assertEqual(current["category"], "unknown")

    async def test_permissions_current_and_previous_assignee_and_reporter(self):
        ticket = await self.create()
        reporter = await self.add_user("category-reporter@mail.com")
        other_staff = await self.add_user("category-staff@mail.com", "staff")
        self.assertEqual((await self.correct(ticket, actor=self.user)).status_code, 403)
        own = await self.client.post("/tickets/", json={"text": "Nie działa sieć."}, headers=self.headers(reporter))
        self.assertEqual(own.status_code, 201)
        self.assertEqual((await self.correct(own.json()["ticket"], actor=reporter)).status_code, 403)
        await self.client.patch(f"/tickets/{ticket['id']}/status", json={"status": "accepted"})
        response = await self.correct(ticket, actor=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["manual_category_by_id"], self.user.id)
        self.assertEqual((await self.correct(ticket, actor=other_staff)).status_code, 403)
        reassigned = await self.client.patch(f"/tickets/{ticket['id']}/assignee", json={"assignee_id": other_staff.id}, headers=self.admin_headers)
        self.assertEqual(reassigned.status_code, 200)
        self.assertEqual((await self.correct(ticket, actor=self.user)).status_code, 403)
        self.assertEqual((await self.correct(ticket, "performance", actor=other_staff)).status_code, 200)
        self.assertEqual((await self.correct(ticket, "bug")).status_code, 200)

    async def test_correction_keeps_priority_workflow_tasks_embedding_and_references(self):
        await self.add_reference()
        ticket = await self.create()
        await self.run_classification(ticket["current_task_id"])
        await self.client.patch(f"/tickets/{ticket['id']}", json={"work_blocked": True})
        manual = await self.client.patch(f"/tickets/{ticket['id']}/priority", json={"priority": "low"}, headers=self.admin_headers)
        self.assertEqual(manual.status_code, 200)
        before = await self.detail(ticket)
        async with self.sessions() as db:
            reference = await db.scalar(text("SELECT jsonb_agg(to_jsonb(classification_references)) FROM classification_references"))
            vector = list((await db.get(Ticket, ticket["id"])).embedding_vector)
        for category in ("bug", "performance", "feature"):
            response = await self.correct(ticket, category)
            self.assertEqual(response.status_code, 200)
            current = response.json()
            self.assertEqual(current["category"], category)
            self.assertEqual(current["manual_category"], category)
            self.assertTrue(current["manual_category_current"])
            self.assertEqual(current["manual_category_version"], current["content_version"])
            self.assertEqual(current["manual_category_by_id"], self.admin.id)
            self.assertIsNotNone(current["manual_category_at"])
            for field in ("status", "text", "author_id", "assignee_id", "current_task_id", "content_version", "embedding_version",
                          "priority", "priority_source", "base_priority", "manual_priority_by_id", "manual_priority_at"):
                self.assertEqual(current[field], before[field], field)
        async with self.sessions() as db:
            self.assertEqual(await db.scalar(text("SELECT jsonb_agg(to_jsonb(classification_references)) FROM classification_references")), reference)
            self.assertEqual(list((await db.get(Ticket, ticket["id"])).embedding_vector), vector)
            self.assertEqual(await db.scalar(text("SELECT count(*) FROM classification_tasks")), 1)
        self.mock_delay.assert_called_once()
        state = (await self.client.get(f"/tickets/{ticket['id']}/task/{ticket['current_task_id']}")).json()
        self.assertEqual(state["state"], "succeeded")
        self.assertEqual(state["result"]["category"], "bug")

    async def test_running_prediction_and_manual_correction_both_completion_orders(self):
        # Opóźniony model oraz wynik zakończony przed korektą muszą dać ten sam stan.
        for first in ("correction", "prediction"):
            ticket = await self.create()
            entered, release = asyncio.Event(), asyncio.Event()

            async def delayed(*args):
                entered.set()
                await release.wait()
                return PREDICTION

            with patch.object(self.runtime, "classifier", side_effect=delayed):
                processing = asyncio.create_task(self.process(ticket["current_task_id"]))
                try:
                    await asyncio.wait_for(entered.wait(), 5)
                    if first == "correction":
                        self.assertEqual((await self.correct(ticket)).status_code, 200)
                finally:
                    release.set()
                    await processing
            if first == "prediction":
                self.assertEqual((await self.correct(ticket)).status_code, 200)
            current = await self.detail(ticket)
            self.assertEqual(current["category"], "feature")
            self.assertEqual(current["predicted_category"], "bug")
            self.assertEqual(current["predicted_category_version"], 1)
            self.assertTrue(current["manual_category_current"])
            state = (await self.client.get(f"/tickets/{ticket['id']}/task/{ticket['current_task_id']}")).json()
            self.assertEqual(state["state"], "succeeded")
            self.assertEqual(state["result"]["category"], "bug")

    async def test_unknown_prediction_cannot_erase_manual_category(self):
        ticket = await self.create()
        self.assertEqual((await self.correct(ticket)).status_code, 200)
        await self.run_classification(ticket["current_task_id"], replace(PREDICTION, category="unknown", base_priority=None, automatic_priority=None))
        current = await self.detail(ticket)
        self.assertEqual(current["category"], "feature")
        self.assertEqual(current["predicted_category"], "unknown")
        self.assertEqual(current["priority_source"], "fallback")
        self.assertEqual(current["priority"], "medium")

    async def test_failed_retry_preserves_category_and_manual_priority(self):
        ticket = await self.create()
        with patch.object(self.runtime, "classifier", side_effect=RuntimeError("Test awarii modelu")):
            await self.process(ticket["current_task_id"])
        self.assertEqual((await self.correct(ticket)).status_code, 200)
        await self.client.patch(f"/tickets/{ticket['id']}/priority", json={"priority": "low"}, headers=self.admin_headers)
        retry = await self.client.post(f"/tickets/{ticket['id']}/classification/retry", headers=self.admin_headers)
        self.assertEqual(retry.status_code, 202)
        await self.run_classification(retry.json()["task_id"])
        current = await self.detail(ticket)
        self.assertEqual(current["category"], "feature")
        self.assertEqual(current["predicted_category"], "bug")
        self.assertEqual(current["priority"], "low")
        self.assertEqual(current["priority_source"], "administrator")

    async def test_text_edit_invalidates_correction_but_checkbox_keeps_it(self):
        ticket = await self.create()
        await self.run_classification(ticket["current_task_id"])
        correction = await self.correct(ticket)
        self.assertEqual(correction.status_code, 200)
        changed = await self.client.patch(f"/tickets/{ticket['id']}", json={"work_blocked": True})
        self.assertEqual(changed.status_code, 200)
        self.assertTrue(changed.json()["ticket"]["manual_category_current"])
        same = await self.client.patch(f"/tickets/{ticket['id']}", json={"text": ticket["text"]})
        self.assertEqual(same.status_code, 200)
        self.assertTrue(same.json()["ticket"]["manual_category_current"])
        edited = await self.client.patch(f"/tickets/{ticket['id']}", json={"text": "Inny opis problemu."})
        self.assertEqual(edited.status_code, 200)
        current = edited.json()["ticket"]
        self.assertEqual(current["content_version"], 2)
        self.assertEqual(current["category"], "unknown")
        self.assertFalse(current["manual_category_current"])
        for field in ("manual_category", "manual_category_version", "manual_category_by_id", "manual_category_at"):
            self.assertEqual(current[field], correction.json()[field])
        self.assertEqual(current["predicted_category_version"], 1)
        await self.run_classification(edited.json()["task_id"], replace(PREDICTION, category="performance"))
        current = await self.detail(ticket)
        self.assertEqual(current["category"], "performance")
        self.assertEqual(current["predicted_category_version"], 2)
        self.assertFalse(current["manual_category_current"])
        self.assertTrue(current["classification_current"])

    async def test_database_rejects_partial_or_unknown_manual_correction(self):
        ticket = await self.create()
        async with self.sessions() as db:
            stored = await db.get(Ticket, ticket["id"])
            stored.manual_category = "feature"
            with self.assertRaises(IntegrityError):
                await db.commit()
        self.assertEqual((await self.correct(ticket)).status_code, 200)
        async with self.sessions() as db:
            stored = await db.get(Ticket, ticket["id"])
            stored.manual_category = "other"
            with self.assertRaises(IntegrityError):
                await db.commit()
