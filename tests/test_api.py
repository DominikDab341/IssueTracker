import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from tests.support import TEST_URL, migration_config
from alembic import command
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.main import app
from app.api.dependencies import get_processing_runtime
from app.database.database import get_db
from app.models.models import ClassificationReference, Ticket, User
from app.services.auth import create_access_token, password_hasher
from app.services.tasks import now
from app.services.classifier import classify, find_similar_open_tickets
from app.services.text_validation import TokenizerUnavailableError, get_tokenizer
from app.ticket_status import ALLOWED_TRANSITIONS, TicketStatus
from app.services.processing import ProcessingRuntime


TEST_PASSWORD = "test-password-for-users"
TEST_PASSWORD_HASH = password_hasher.hash(TEST_PASSWORD)


def setUpModule():
    command.upgrade(migration_config(), "head")


class ApiTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine(TEST_URL)
        self.sessions = async_sessionmaker(self.engine, expire_on_commit=False)
        async with self.engine.begin() as connection:
            await connection.execute(text("TRUNCATE assignment_history, classification_references, classification_tasks, tickets, users RESTART IDENTITY"))

        self.user = await self.add_user("staff@mail.com", "staff")
        self.admin = await self.add_user("admin@mail.com", "admin")
        self.admin_headers = self.headers(self.admin)

        async def database_override():
            async with self.sessions() as session:
                yield session

        app.dependency_overrides[get_db] = database_override
        self.classifier = AsyncMock(wraps=classify)
        self.runtime = ProcessingRuntime(self.sessions, classifier=self.classifier)
        self.process = self.runtime.process
        app.dependency_overrides[get_processing_runtime] = lambda: self.runtime
        self.delay = patch.object(self.runtime, "process")
        self.mock_delay = self.delay.start()
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        self.client.headers.update(self.headers(self.user))

    @staticmethod
    def headers(user):
        return {"Authorization": "Bearer " + create_access_token(user.id)}

    async def add_user(self, email, role="reporter", active=True, approved=True):
        async with self.sessions() as db:
            user = User(email=email, role=role if approved else None,
                        password_hash=TEST_PASSWORD_HASH, is_active=active, is_approved=approved,
                        approved_at=now() if approved else None)
            db.add(user)
            await db.commit()
            return user

    async def asyncTearDown(self):
        await self.client.aclose()
        app.dependency_overrides.clear()
        self.delay.stop()
        await self.engine.dispose()

    async def create(self, description="Nie mogę połączyć się z drukarką."):
        response = await self.client.post("/tickets/", json={"text": description})
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["ticket"]

    async def add_ticket(self, status="reported", category="bug", priority="medium", embedding=None, created_at=None):
        async with self.sessions() as session:
            ticket = Ticket(text="Problem z aplikacją.", status=status, category=category, priority=priority,
                            author_id=self.user.id,
                            assignee_id=self.user.id if status in ("accepted", "in_progress") else None,
                            embedding_vector=embedding, embedding_version=1 if embedding is not None else None)
            if created_at is not None:
                ticket.created_at = created_at
            session.add(ticket)
            await session.commit()
            await session.refresh(ticket)
            return ticket.id

    async def add_reference(self, category="bug", base_priority="low", embedding=None):
        async with self.sessions() as session:
            reference = ClassificationReference(
                text="Sprawdzony przykład.", category=category, base_priority=base_priority,
                embedding_vector=embedding if embedding is not None else [1.0] + [0.0] * 383,
                source="test", source_key=str(uuid4()),
            )
            session.add(reference)
            await session.commit()
            return reference.id

class TicketApiTests(ApiTestCase):
    async def test_create_get_list_and_no_vector(self):
        ticket = await self.create("  Nie działa drukarka.  ")
        self.assertEqual(ticket["text"], "Nie działa drukarka.")
        self.assertEqual(ticket["status"], "reported")
        self.assertNotIn("embedding_vector", ticket)
        self.mock_delay.assert_called_once_with(ticket["current_task_id"])
        detail = await self.client.get(f"/tickets/{ticket['id']}")
        self.assertEqual(detail.json(), ticket)
        self.assertEqual((await self.client.get("/tickets/")).json(), [ticket])

    async def test_missing_tickets(self):
        for method, path, body in [
            ("GET", "/tickets/999", None),
            ("PATCH", "/tickets/999/status", {"status": "accepted"}),
            ("DELETE", "/tickets/999", {"status": "cancelled"}),
        ]:
            response = await self.client.request(method, path, json=body)
            self.assertEqual(response.status_code, 404)

    async def test_invalid_text_and_payload(self):
        for body in [{}, {"text": ""}, {"text": " \n\t "}, {"text": None}, {"text": 42}, {"text": "x" * 10001}, {"text": "drukarka " * 300}, {"text": "Opis", "status": "resolved"}]:
            response = await self.client.post("/tickets/", json=body)
            self.assertEqual(response.status_code, 422, str(body))
        self.mock_delay.assert_not_called()
        self.assertEqual((await self.client.get("/tickets/")).json(), [])

    async def test_real_tokenizer_boundary(self):
        tokenizer = get_tokenizer()
        at_limit = "test " * 254
        self.assertEqual(len(tokenizer.encode(at_limit, add_special_tokens=True, truncation=False)), 256)
        await self.create(at_limit)
        response = await self.client.post("/tickets/", json={"text": at_limit + "test"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("257", response.text)

    async def test_tokenizer_unavailable_does_not_create_ticket(self):
        with patch("app.services.text_validation.get_tokenizer", side_effect=TokenizerUnavailableError("Tokenizer modelu jest niedostępny.")):
            response = await self.client.post("/tickets/", json={"text": "Problem z drukarką."})
        self.assertEqual(response.status_code, 503)
        self.assertEqual((await self.client.get("/tickets/")).json(), [])
        self.mock_delay.assert_not_called()

    async def test_filters_pagination_and_stable_order(self):
        date = datetime(2026, 1, 1, tzinfo=timezone.utc)
        ids = [await self.add_ticket(category="bug", priority="high", created_at=date) for _ in range(4)]
        await self.add_ticket(status="rejected", category="feature", priority="low", created_at=date)
        url = "/tickets/?status=reported&category=bug&priority=high&limit=2"
        first = (await self.client.get(url)).json()
        second = (await self.client.get(url + "&offset=2")).json()
        self.assertEqual([t["id"] for t in first + second], list(reversed(ids)))
        self.assertEqual((await self.client.get(url + "&offset=4")).json(), [])
        for query in ["limit=0", "limit=101", "offset=-1", "status=open", "priority=urgent", "category=", "limit=abc"]:
            self.assertEqual((await self.client.get("/tickets/?" + query)).status_code, 422, query)

    async def test_all_status_transitions(self):
        for source in TicketStatus:
            for target in TicketStatus:
                with self.subTest(source=source, target=target):
                    ticket_id = await self.add_ticket(status=source)
                    body = {"status": target}
                    if target == "resolved":
                        body["resolution_note"] = "Ponownie zainstalowano sterownik."
                    if target == "rejected":
                        body["rejection_reason"] = "Zgłoszenie dotyczy tej samej awarii."
                    response = await self.client.patch(f"/tickets/{ticket_id}/status", json=body,
                                                        headers=self.admin_headers if target not in ("accepted", "cancelled") else None)
                    allowed = target in ALLOWED_TRANSITIONS[source]
                    self.assertEqual(response.status_code, 200 if allowed else 409, response.text)
                    actual = (await self.client.get(f"/tickets/{ticket_id}")).json()
                    self.assertEqual(actual["status"], target if allowed else source)
                    self.assertNotIn("embedding_vector", actual)
        self.mock_delay.assert_not_called()

    async def test_notes_required_and_saved_atomically(self):
        for source, target, note_field in [("in_progress", "resolved", "resolution_note"), ("reported", "rejected", "rejection_reason")]:
            ticket_id = await self.add_ticket(status=source)
            for note in [None, " \t "]:
                response = await self.client.patch(f"/tickets/{ticket_id}/status", json={"status": target, note_field: note})
                self.assertEqual(response.status_code, 422)
                self.assertEqual((await self.client.get(f"/tickets/{ticket_id}")).json()["status"], source)
            response = await self.client.patch(f"/tickets/{ticket_id}/status", json={"status": target, note_field: "  Uzasadnienie.  "})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()[note_field], "Uzasadnienie.")
            self.assertIsNotNone(response.json()["resolved_at" if target == "resolved" else "rejected_at"])

    async def test_delete_alias_preserves_history_and_obeys_workflow(self):
        ticket = await self.create()
        ticket_id = ticket["id"]
        self.assertEqual((await self.client.delete(f"/tickets/{ticket_id}")).status_code, 422)
        self.assertEqual((await self.client.request("DELETE", f"/tickets/{ticket_id}", json={"status": "accepted"})).status_code, 422)
        self.assertEqual((await self.client.request("DELETE", f"/tickets/{ticket_id}", json={"status": "resolved", "resolution_note": "Opis"})).status_code, 409)
        response = await self.client.request("DELETE", f"/tickets/{ticket_id}", json={"status": "cancelled"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["suggested_duplicates"], [])
        self.assertNotIn("embedding_vector", response.json()["ticket"])
        self.assertEqual((await self.client.get(f"/tickets/{ticket_id}")).json()["status"], "cancelled")
        self.assertEqual((await self.client.request("DELETE", f"/tickets/{ticket_id}", json={"status": "cancelled"})).status_code, 409)
        new_ticket = await self.create()
        self.assertNotEqual(new_ticket["id"], ticket_id)
        self.assertEqual(len((await self.client.get("/tickets/")).json()), 2)

    async def test_concurrent_transitions_cannot_reopen_terminal_ticket(self):
        ticket_id = await self.add_ticket()
        path = f"/tickets/{ticket_id}/status"
        responses = await asyncio.gather(
            self.client.patch(path, json={"status": "cancelled"}),
            self.client.patch(path, json={"status": "accepted"}),
        )
        self.assertEqual(sorted(r.status_code for r in responses), [200, 409])

    async def test_duplicates_use_pgvector_and_only_active_statuses(self):
        vector = [1.0] + [0.0] * 383
        source = await self.add_ticket(embedding=vector)
        active = [await self.add_ticket(status=s, embedding=vector) for s in ["reported", "accepted", "in_progress"]]
        for status in ["resolved", "rejected", "cancelled"]:
            await self.add_ticket(status=status, embedding=vector)
        async with self.sessions() as session:
            result = await find_similar_open_tickets(source, vector, "bug", session, actor=self.user)
            self.assertEqual({row["id"] for row in result}, set(active))
            self.assertTrue(all(row["similarity"] == 1.0 for row in result))

    async def test_seed_uses_migrated_schema_and_skips_existing_data(self):
        from scripts import seed_db
        vector = SimpleNamespace(tolist=lambda: [1.0] + [0.0] * 383)
        model = SimpleNamespace(encode=lambda value: vector)
        with patch.object(seed_db, "engine", self.engine), patch.object(seed_db, "get_model", return_value=model) as load:
            await seed_db.seed_tickets(self.user.email)
            first = (await self.client.get("/tickets/?limit=100")).json()
            self.assertEqual(len(first), 10)
            self.assertTrue(all(ticket["status"] == "reported" for ticket in first))
            self.assertTrue(all(ticket["classification_current"] for ticket in first))
            async with self.sessions() as session:
                references = await session.scalar(text("SELECT count(*) FROM classification_references"))
                self.assertEqual(references, 10)
            seeded = first[0]
            await self.client.patch(f"/tickets/{seeded['id']}", json={"work_blocked": True})
            restored = await self.client.patch(f"/tickets/{seeded['id']}", json={"work_blocked": False})
            self.assertEqual(restored.json()["ticket"]["priority"], seeded["priority"])
            first = (await self.client.get("/tickets/?limit=100")).json()
            load.reset_mock()
            await seed_db.seed_tickets()
            load.assert_not_called()
            self.assertEqual((await self.client.get("/tickets/?limit=100")).json(), first)

    async def test_seed_adds_references_without_modifying_existing_tickets(self):
        from scripts import seed_db
        await self.add_ticket(priority="critical", embedding=[1.0] + [0.0] * 383)
        before = (await self.client.get("/tickets/")).json()
        model = SimpleNamespace(encode=lambda value: SimpleNamespace(tolist=lambda: [1.0] + [0.0] * 383))
        with patch.object(seed_db, "engine", self.engine), patch.object(seed_db, "get_model", return_value=model):
            await seed_db.seed_tickets()
        self.assertEqual((await self.client.get("/tickets/")).json(), before)
        async with self.sessions() as session:
            self.assertEqual(await session.scalar(text("SELECT count(*) FROM classification_references")), 10)
            self.assertEqual(await session.scalar(text("SELECT count(*) FROM classification_references WHERE source='sample_tickets'")), 10)

    async def test_seed_default_adds_only_references_and_no_unowned_tickets(self):
        from scripts import seed_db
        model = SimpleNamespace(encode=lambda value: SimpleNamespace(tolist=lambda: [1.0] + [0.0] * 383))
        with patch.object(seed_db, "engine", self.engine), patch.object(seed_db, "get_model", return_value=model):
            await seed_db.seed_tickets()
        async with self.sessions() as session:
            self.assertEqual(await session.scalar(text("SELECT count(*) FROM tickets")), 0)
            self.assertEqual(await session.scalar(text("SELECT count(*) FROM classification_references")), 10)


if __name__ == "__main__":
    unittest.main()
