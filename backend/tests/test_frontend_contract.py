"""Odczyty potrzebne aplikacji React, na osobnej bazie PostgreSQL/pgvector."""
from unittest.mock import patch

from sqlalchemy import select

from tests.test_api import ApiTestCase, setUpModule
from app.models.models import Ticket


class FrontendContractTests(ApiTestCase):
    async def test_public_domain_and_explicit_cors(self):
        self.client.headers.pop("Authorization")
        with patch("app.api.auth.settings.ALLOWED_EMAIL_DOMAIN", "Example.PL"):
            response = await self.client.get("/auth/config")
        self.assertEqual(response.json(), {"allowed_email_domain": "example.pl"})
        self.assertNotIn("secret", response.text.lower())
        for origin, status in [("http://localhost:5173", 200), ("http://localhost:3000", 200),
                               ("https://untrusted.example", 400)]:
            response = await self.client.options("/tickets/1", headers={
                "Origin": origin, "Access-Control-Request-Method": "PATCH",
                "Access-Control-Request-Headers": "authorization,content-type",
            })
            self.assertEqual(response.status_code, status)
            self.assertEqual(response.headers.get("access-control-allow-origin"), origin if status == 200 else None)

    async def test_review_filter_and_task_state_do_not_change_visibility(self):
        reporter = await self.add_user("reporter@mail.com")
        self.client.headers.update(self.headers(reporter))
        ticket = await self.create()
        detail = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertTrue(detail["needs_review"])
        self.assertEqual(detail["current_task_state"], "pending")
        self.assertEqual(ticket, detail)
        self.assertEqual((await self.client.get("/tickets/?needs_review=true")).status_code, 403)
        self.client.headers.update(self.headers(self.user))
        known = await self.add_ticket(category="bug")
        review = (await self.client.get("/tickets/?needs_review=true")).json()
        self.assertEqual([row["id"] for row in review], [ticket["id"]])
        self.assertEqual([row["id"] for row in (await self.client.get("/tickets/?needs_review=false")).json()], [known])
        self.assertEqual((await self.client.get("/tickets/?needs_review=invalid")).status_code, 422)
        self.client.headers.update(self.headers(reporter))
        self.assertEqual([row["id"] for row in (await self.client.get("/tickets/")).json()], [ticket["id"]])
        with patch("app.services.classifier.encode_text", return_value=[1.0] + [0.0] * 383):
            await self.process(ticket["current_task_id"])
        detail = (await self.client.get(f"/tickets/{ticket['id']}")).json()
        self.assertEqual(detail["current_task_state"], "succeeded")
        self.assertTrue(detail["needs_review"])  # Brak referencji nie jest awarią zadania.

    async def test_duplicates_require_access_and_current_embeddings(self):
        vector = [1.0] + [0.0] * 383
        source = await self.add_ticket(embedding=vector)
        visible = await self.add_ticket(embedding=vector)
        stale = await self.add_ticket(embedding=vector)
        hidden = await self.add_ticket(embedding=vector)
        reporter = await self.add_user("reporter@mail.com")
        async with self.sessions() as db:
            for ticket in (await db.scalars(select(Ticket).where(Ticket.id.in_([source, visible, stale])))).all():
                ticket.author_id = reporter.id
                if ticket.id == stale:
                    ticket.content_version = 2
            await db.commit()
        response = await self.client.get(f"/tickets/{source}/duplicates", headers=self.headers(reporter))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.json()], [visible])
        self.assertNotIn("embedding", response.text)
        self.assertEqual((await self.client.get(f"/tickets/{hidden}/duplicates", headers=self.headers(reporter))).status_code, 404)
        self.assertEqual((await self.client.get(f"/tickets/{stale}/duplicates", headers=self.headers(reporter))).json(), [])
        self.client.headers.pop("Authorization")
        self.assertEqual((await self.client.get(f"/tickets/{source}/duplicates")).status_code, 401)

    async def test_assignee_directory_only_contains_eligible_staff(self):
        await self.add_user("inactive@mail.com", "staff", active=False)
        await self.add_user("pending@mail.com", "staff", approved=False)
        await self.add_user("reporter@mail.com", "reporter")
        second = await self.add_user("zzz@mail.com", "staff")
        self.assertEqual((await self.client.get("/admin/assignees")).status_code, 403)
        response = await self.client.get("/admin/assignees?limit=1&offset=1", headers=self.admin_headers)
        self.assertEqual(response.json(), [{"id": second.id, "email": second.email}])
        for query in ["limit=0", "limit=101", "offset=-1"]:
            self.assertEqual((await self.client.get("/admin/assignees?" + query, headers=self.admin_headers)).status_code, 422)
