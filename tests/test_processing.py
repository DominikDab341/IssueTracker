import asyncio
from threading import Event, Lock
import time
from unittest.mock import patch

from sqlalchemy import select, text

from app.models.models import ClassificationTask, Ticket
from app.services.processing import ProcessingRuntime
from tests.test_api import ApiTestCase, setUpModule


VECTOR = [1.0] + [0.0] * 383
PREDICTION = {"category": "feature", "base_priority": "low", "priority": "high", "vector": VECTOR}


class ProcessingTests(ApiTestCase):
    async def new(self, blocked=False):
        response = await self.client.post("/tickets/", json={"text": "Nie działa drukarka.", "work_blocked": blocked})
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["ticket"]

    async def status(self, ticket, task_id=None):
        response = await self.client.get(f"/tickets/{ticket['id']}/task/{task_id or ticket['current_task_id']}")
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    async def detail(self, ticket):
        return (await self.client.get(f"/tickets/{ticket['id']}")).json()

    async def test_create_commit_precedes_dispatch_and_failure_is_atomic(self):
        async def observe(task_id):
            async with self.sessions() as db:
                task = await db.get(ClassificationTask, task_id)
                self.assertIsNotNone(task)
                self.assertEqual(task.state, "pending")
                self.assertIsNotNone(await db.get(Ticket, task.ticket_id))

        self.mock_delay.side_effect = observe
        await self.new()
        with patch("app.api.main.create_task", side_effect=RuntimeError("Test rollback")):
            with self.assertRaises(RuntimeError):
                await self.new()
        async with self.sessions() as db:
            self.assertEqual(await db.scalar(text("SELECT count(*) FROM tickets")), 1)
            self.assertEqual(await db.scalar(text("SELECT count(*) FROM classification_tasks")), 1)
        self.mock_delay.assert_awaited_once()

    async def test_persisted_pending_and_success_priority_precedence(self):
        for blocked, expected in [(False, "high"), (True, "critical")]:
            ticket = await self.new(blocked)
            self.assertEqual(ticket["priority"], "critical" if blocked else "medium")
            self.assertEqual((await self.status(ticket))["state"], "pending")
            with patch("app.services.processing.classify", return_value=PREDICTION):
                await self.process(ticket["current_task_id"])
            state = await self.status(ticket)
            result = await self.detail(ticket)
            self.assertEqual(state["state"], "succeeded")
            self.assertTrue(state["current"])
            self.assertIsNotNone(state["started_at"])
            self.assertIsNotNone(state["finished_at"])
            self.assertNotIn("vector", state["result"])
            self.assertEqual(result["status"], "reported")
            self.assertEqual(result["base_priority"], "low")
            self.assertEqual(result["priority"], expected)
            self.assertTrue(result["classification_current"])
            retry = await self.client.post(f"/tickets/{ticket['id']}/classification/retry")
            self.assertEqual(retry.status_code, 409)

    async def test_task_lookup_checks_ticket_and_missing(self):
        first, second = await self.new(), await self.new()
        for path in [f"/tickets/{second['id']}/task/{first['current_task_id']}",
                     f"/tickets/{first['id']}/task/missing", "/tickets/999/task/missing"]:
            self.assertEqual((await self.client.get(path)).status_code, 404)

    async def test_model_failure_safe_error_and_concurrent_retry(self):
        ticket = await self.new(True)
        with patch("app.services.processing.classify", side_effect=RuntimeError("SECRET model path and credentials")):
            await self.process(ticket["current_task_id"])
        state = await self.status(ticket)
        self.assertEqual(state["state"], "failed")
        self.assertEqual(state["error_code"], "processing_failed")
        self.assertNotIn("SECRET", str(state))
        responses = await asyncio.gather(*[self.client.post(f"/tickets/{ticket['id']}/classification/retry") for _ in range(2)])
        self.assertEqual(sorted(r.status_code for r in responses), [202, 409])
        retried = next(r.json()["ticket"] for r in responses if r.status_code == 202)
        self.assertNotEqual(retried["current_task_id"], ticket["current_task_id"])
        with patch("app.services.processing.classify", return_value=PREDICTION):
            await self.process(retried["current_task_id"])
        self.assertEqual((await self.status(retried))["state"], "succeeded")
        self.assertEqual((await self.detail(retried))["priority"], "critical")
        self.assertFalse((await self.status(ticket))["current"])

    async def test_failed_database_write_rolls_back_prediction(self):
        ticket = await self.new()
        # pgvector rejects a bad dimension at flush: neither category nor success may persist.
        with patch("app.services.processing.classify", return_value={**PREDICTION, "vector": [1.0]}):
            await self.process(ticket["current_task_id"])
        state = await self.status(ticket)
        detail = await self.detail(ticket)
        self.assertEqual(state["state"], "failed")
        self.assertEqual(state["error_code"], "processing_failed")
        self.assertIsNone(state["result"])
        self.assertEqual(detail["category"], "unknown")
        self.assertIsNone(detail["embedding_version"])

    async def test_edit_running_version_ignores_late_result(self):
        ticket = await self.new()
        entered, release = asyncio.Event(), asyncio.Event()

        async def delayed(*args, **kwargs):
            entered.set()
            await release.wait()
            return PREDICTION

        with patch("app.services.processing.classify", side_effect=delayed):
            processing = asyncio.create_task(self.process(ticket["current_task_id"]))
            await asyncio.wait_for(entered.wait(), 5)
            self.assertEqual((await self.status(ticket))["state"], "running")
            edit = await self.client.patch(f"/tickets/{ticket['id']}", json={"text": "Nie działa sieć."})
            self.assertEqual(edit.status_code, 200, edit.text)
            release.set()
            await processing
        changed = edit.json()["ticket"]
        self.assertEqual(changed["content_version"], 2)
        self.assertFalse(changed["classification_current"])
        self.assertEqual((await self.status(ticket))["error_code"], "superseded")
        self.assertFalse((await self.status(ticket))["current"])
        self.assertEqual((await self.detail(ticket))["category"], "unknown")
        with patch("app.services.processing.classify", return_value=PREDICTION):
            await self.process(changed["current_task_id"])
        self.assertEqual((await self.detail(ticket))["embedding_version"], 2)

    async def test_checkbox_only_keeps_embedding_and_manual_decision(self):
        ticket = await self.new()
        with patch("app.services.processing.classify", return_value=PREDICTION):
            await self.process(ticket["current_task_id"])
        calls = self.mock_delay.call_count
        response = await self.client.patch(f"/tickets/{ticket['id']}", json={"work_blocked": True})
        changed = response.json()["ticket"]
        self.assertEqual(changed["priority"], "critical")
        self.assertEqual(changed["embedding_version"], 1)
        self.assertEqual(changed["current_task_id"], ticket["current_task_id"])
        self.assertEqual(self.mock_delay.call_count, calls)
        async with self.sessions() as db:
            row = await db.get(Ticket, ticket["id"])
            row.manual_priority = "low"  # Future E5.9 decision, no public endpoint introduced here.
            await db.commit()
        response = await self.client.patch(f"/tickets/{ticket['id']}", json={"text": "Nowy opis problemu.", "work_blocked": True})
        changed = response.json()["ticket"]
        with patch("app.services.processing.classify", return_value=PREDICTION):
            await self.process(changed["current_task_id"])
        result = await self.detail(ticket)
        self.assertEqual(result["priority"], "low")
        self.assertEqual(result["priority_source"], "administrator")

    async def test_manual_decision_during_computation_and_terminal_result(self):
        ticket = await self.new(True)
        await self.runtime._claim(ticket["current_task_id"])
        async with self.sessions() as db:
            row = await db.get(Ticket, ticket["id"])
            row.manual_priority = "low"
            await db.commit()
        await self.runtime._save_result(ticket["current_task_id"], PREDICTION)
        self.assertEqual((await self.detail(ticket))["priority"], "low")
        another = await self.new()
        await self.runtime._claim(another["current_task_id"])
        response = await self.client.patch(f"/tickets/{another['id']}/status", json={"status": "cancelled"})
        self.assertEqual(response.status_code, 200)
        await self.runtime._save_result(another["current_task_id"], PREDICTION)
        self.assertEqual((await self.status(another))["error_code"], "obsolete")
        detail = await self.detail(another)
        self.assertEqual(detail["status"], "cancelled")
        self.assertEqual(detail["category"], "unknown")
        self.assertEqual((await self.client.post(f"/tickets/{another['id']}/classification/retry")).status_code, 409)

    async def test_edit_accept_race_and_validation(self):
        ticket = await self.new()
        for body in [{}, {"text": None}, {"work_blocked": None}, {"work_blocked": "yes"},
                     {"text": " "}, {"manual_priority": "low"}]:
            self.assertEqual((await self.client.patch(f"/tickets/{ticket['id']}", json=body)).status_code, 422)
        same = await self.client.patch(f"/tickets/{ticket['id']}", json={"text": ticket["text"]})
        self.assertEqual(same.json()["ticket"]["content_version"], 1)
        edit, accept = await asyncio.gather(
            self.client.patch(f"/tickets/{ticket['id']}", json={"text": "Inny opis."}),
            self.client.patch(f"/tickets/{ticket['id']}/status", json={"status": "accepted"}),
        )
        self.assertEqual(accept.status_code, 200)
        self.assertIn(edit.status_code, (200, 409))
        after = await self.client.patch(f"/tickets/{ticket['id']}", json={"work_blocked": True})
        self.assertEqual(after.status_code, 409)
        if edit.status_code == 409:
            self.assertEqual((await self.detail(ticket))["text"], ticket["text"])
        self.assertEqual((await self.client.post(f"/tickets/{ticket['id']}/classification/retry")).status_code, 409)

    async def test_thread_responsiveness_serial_computation_and_sequential_tickets(self):
        await self.add_ticket(category="feature", priority="low", embedding=VECTOR)
        first, second = await self.new(), await self.new()
        entered, release = Event(), Event()
        lock = Lock()
        active, maximum = 0, 0

        def encoder(description):
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
            entered.set()
            release.wait(10)
            with lock:
                active -= 1
            return VECTOR

        with patch("app.services.classifier.encode_text", side_effect=encoder):
            tasks = [asyncio.create_task(self.process(t["current_task_id"])) for t in [first, second]]
            try:
                deadline = time.monotonic() + 5
                while not entered.is_set() and time.monotonic() < deadline:
                    await asyncio.sleep(.01)
                self.assertTrue(entered.is_set())
                detail = await asyncio.wait_for(self.client.get(f"/tickets/{first['id']}"), 2)
                self.assertEqual(detail.status_code, 200)
                self.assertEqual((await self.status(first))["state"], "running")
                self.assertEqual((await self.status(second))["state"], "pending")
            finally:
                release.set()
                await asyncio.gather(*tasks)
        self.assertEqual(maximum, 1)
        for ticket in [first, second]:
            self.assertEqual((await self.status(ticket))["state"], "succeeded")
        third = await self.new()
        with patch("app.services.classifier.encode_text", return_value=VECTOR):
            await self.process(third["current_task_id"])
        self.assertEqual((await self.status(third))["state"], "succeeded")

    async def test_second_process_refused_restart_recovers_orphans(self):
        await self.runtime.start(self.engine)
        other = ProcessingRuntime(self.sessions)
        replacement = ProcessingRuntime(self.sessions)
        try:
            first, second = await self.new(), await self.new()
            await self.runtime._claim(first["current_task_id"])
            with self.assertRaises(RuntimeError):
                await other.start(self.engine)
            self.assertEqual((await self.status(first))["state"], "running")
            self.assertEqual((await self.status(second))["state"], "pending")
            await self.runtime.stop()
            await replacement.start(self.engine)
            for ticket in [first, second]:
                state = await self.status(ticket)
                self.assertEqual(state["state"], "failed")
                self.assertEqual(state["error_code"], "interrupted")
            await self.runtime._save_result(first["current_task_id"], PREDICTION)
            self.assertEqual((await self.detail(first))["category"], "unknown")
        finally:
            await other.stop()
            await replacement.stop()
            await self.runtime.stop()

    async def test_stale_embeddings_excluded_and_empty_reference_succeeds(self):
        reference = await self.add_ticket(embedding=VECTOR)
        async with self.sessions() as db:
            row = await db.get(Ticket, reference)
            row.content_version = 2
            await db.commit()
        ticket = await self.new()
        with patch("app.services.classifier.encode_text", return_value=VECTOR):
            await self.process(ticket["current_task_id"])
        result = await self.detail(ticket)
        self.assertEqual(result["category"], "unknown")
        self.assertEqual(result["priority"], "medium")
        self.assertEqual(result["priority_source"], "fallback")
        self.assertEqual((await self.status(ticket))["state"], "succeeded")
        self.assertEqual((await self.client.post(f"/tickets/{ticket['id']}/classification/retry")).status_code, 409)
