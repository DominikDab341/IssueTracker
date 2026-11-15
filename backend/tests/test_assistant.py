from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from tests.test_api import ApiTestCase, setUpModule
from app.models.models import Ticket
from app.services.assistant import AnswerPart, ModelAnswer, ModelUnavailableError, NO_CONTEXT
from app.services.ticket_search import SearchMethod, search_tickets
from app.services.ticket_statistics import GUIDANCE


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
        ticket_ids = [await self.add_case() for _ in range(6)]
        ticket_id = ticket_ids[4]
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
            self.assertEqual([hit.id for hit in fake.await_args.args[2]], ticket_ids[:5])
            fake.return_value = ModelAnswer(status="answered", parts=[
                AnswerPart(text="A source outside the context", ticket_id=ticket_ids[5]),
            ])
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

    async def test_follow_up_reuses_earlier_turns_and_rechecks_sources(self):
        first = await self.add_case()
        newest = await self.add_case()
        stale = await self.add_case(current=False)
        answer = ModelAnswer(status="answered", parts=[AnswerPart(text="Try this first.", ticket_id=first)])
        history = [
            {"question": QUESTION, "parts": [{"text": "Update the client.", "ticket_id": first}]},
            {"question": "Were there alternatives?", "parts": [{"text": "Try a different client.", "ticket_id": stale}]},
            {"question": "What else worked?", "parts": [{"text": "Change the settings.", "ticket_id": newest}]},
        ]
        with patch("app.api.assistant.search_tickets", new_callable=AsyncMock) as search, \
             patch("app.api.assistant.generate_answer", new_callable=AsyncMock, return_value=answer) as generate:
            response = await self.client.post("/assistant/chat", json={
                "question": "Which of these fixes should I try first?",
                "previous_turns": history,
            })
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["parts"], [answer.parts[0].model_dump()])
            _, _, hits, turns = generate.await_args.args
            self.assertEqual([hit.id for hit in hits], [newest, first])
            self.assertEqual([[part.ticket_id for part in turn.parts] for turn in turns], [[first], [], [newest]])
            search.assert_not_awaited()

    async def test_statistics_use_all_visible_statuses_and_local_month_boundaries(self):
        for category, created_at, status in (
            ("network", "2026-10-31T23:00:00+00:00", "reported"),
            ("network", "2026-10-31T22:59:59+00:00", "reported"),
            ("network", "2026-10-03T00:00:00+00:00", "rejected"),
            ("hardware", "2026-10-15T00:00:00+00:00", "in_progress"),
            ("network", "2026-09-30T21:59:59+00:00", "cancelled"),
        ):
            await self.add_ticket(category=category, status=status, created_at=datetime.fromisoformat(created_at))
        reporter = await self.add_user("statistics-reporter@mail.com")
        with patch("app.services.ticket_statistics.now", return_value=datetime(2026, 11, 14, tzinfo=timezone.utc)), \
             patch("app.api.assistant.retrieval_query") as retrieval:
            async def ask(question, headers=None):
                return await self.client.post("/assistant/chat", headers=headers,
                                              json={"question": question, "resolved_only": True})

            ranking = await ask("Which ticket category had the most reports last month?")
            self.assertEqual(ranking.status_code, 200, ranking.text)
            self.assertEqual(ranking.json(), {
                "parts": [],
                "message": "Tickets created · 2026-10-01 to 2026-10-31 (Europe/Warsaw)\n"
                           "All tickets: 3\nNetwork and connectivity: 2\nHardware: 1",
            })
            comparison = await ask("Did network issues increase compared with the previous month?", self.admin_headers)
            self.assertIn("2026-09-01 to 2026-09-30", comparison.json()["message"])
            self.assertIn("Network and connectivity: 2 vs 1 (+1, +100.0%)", comparison.json()["message"])
            partial = await ask("Compare hardware tickets this month with last month")
            self.assertIn("current period to date", partial.json()["message"])
            self.assertIn("Hardware: 0 vs 1 (-1, -100.0%)", partial.json()["message"])
            self.assertEqual((await ask("How many VPN tickets were created last month?")).json()["message"], GUIDANCE)
            denied = await ask("How many tickets were created last month?", self.headers(reporter))
            self.assertEqual(denied.status_code, 403)
            retrieval.assert_not_called()

    async def test_statistics_report_zero_baseline_without_percentage(self):
        await self.add_ticket(category="software", created_at=datetime(2026, 11, 2, tzinfo=timezone.utc))
        with patch("app.services.ticket_statistics.now", return_value=datetime(2026, 11, 14, tzinfo=timezone.utc)):
            response = await self.client.post("/assistant/chat", json={
                "question": "Compare software issues this month and last month",
            })
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("Software: 1 vs 0 (+1, percentage unavailable", response.json()["message"])
