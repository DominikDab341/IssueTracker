from unittest.mock import AsyncMock, patch

from tests.test_api import ApiTestCase, setUpModule
from app.models.models import Ticket
from app.services.assistant import AnswerPart, ModelAnswer, ModelUnavailableError, NO_CONTEXT
from app.services.ticket_search import SearchMethod, search_tickets


VECTOR = [1.0] + [0.0] * 383
QUESTION = "How did we fix VPN disconnects?"


class AssistantTests(ApiTestCase):
    async def add_case(self, *, status="resolved", current=True, text="The VPN disconnects after sleep."):
        async with self.sessions.begin() as db:
            ticket = Ticket(text=text, category="network", priority="medium",
                            status=status, author_id=self.user.id,
                            resolution_note="Updated the VPN client." if status == "resolved" else None,
                            embedding_vector=VECTOR, embedding_version=1,
                            content_version=1 if current else 2)
            db.add(ticket)
            await db.flush()
            return ticket.id

    async def test_both_rankers_filter_status_versions_and_access_before_limit(self):
        await self.add_case(status="reported")
        await self.add_case(current=False)
        expected = await self.add_case()
        reporter = await self.add_user("reporter@mail.com")
        with patch("app.services.ticket_search.encode_text", return_value=VECTOR):
            async with self.sessions() as db:
                for method in SearchMethod:
                    result = await search_tickets(db, self.user, QUESTION, method=method, limit=1)
                    self.assertEqual([hit.id for hit in result.hits], [expected])
                    self.assertEqual(result.hits[0].resolution_note, "Updated the VPN client.")
                    denied = await search_tickets(db, reporter, QUESTION, method=method)
                    self.assertEqual(denied.hits, [])

    async def test_chat_enforces_role_and_citation_membership(self):
        ticket_id = await self.add_case()
        reporter = await self.add_user("reporter@mail.com")
        allowed = ModelAnswer(status="answered", parts=[AnswerPart(text="Updated the VPN client.", ticket_id=ticket_id)])
        fake = AsyncMock(return_value=allowed)
        with patch("app.api.assistant.retrieval_query", return_value=QUESTION), \
             patch("app.services.ticket_search.encode_text", return_value=VECTOR), \
             patch("app.api.assistant.generate_answer", fake):
            denied = await self.client.post("/assistant/chat", json={"question": QUESTION}, headers=self.headers(reporter))
            self.assertEqual(denied.status_code, 403)
            fake.assert_not_called()
            answer = await self.client.post("/assistant/chat", json={"question": QUESTION})
            self.assertEqual(answer.json()["parts"], [allowed.parts[0].model_dump()])
            fake.return_value = ModelAnswer(status="answered", parts=[AnswerPart(text="Unknown source", ticket_id=999)])
            rejected = await self.client.post("/assistant/chat", json={"question": QUESTION})
            self.assertEqual(rejected.json(), {"parts": [], "message": NO_CONTEXT})
            fake.side_effect = ModelUnavailableError("Unavailable")
            offline = await self.client.post("/assistant/chat", json={"question": QUESTION}, headers=self.admin_headers)
            self.assertEqual(offline.status_code, 503)

    async def test_missing_sources_skip_the_model(self):
        await self.add_case(status="reported")
        with patch("app.api.assistant.retrieval_query", return_value=QUESTION), \
             patch("app.services.ticket_search.encode_text", return_value=VECTOR), \
             patch("app.api.assistant.generate_answer", new_callable=AsyncMock) as generate:
            response = await self.client.post("/assistant/chat", json={"question": QUESTION})
        self.assertEqual(response.json(), {"parts": [], "message": NO_CONTEXT})
        generate.assert_not_called()
