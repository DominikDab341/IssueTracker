import asyncio
from unittest.mock import patch

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from tests.test_api import ApiTestCase, setUpModule
from app.domain import ClassificationPrediction, Priority
from app.models.models import ClassificationTask, Ticket
from app.services.classifier import find_similar_open_tickets
from app.services.errors import InvalidInputError
from scripts.import_ticket_authors import import_authors

VECTOR = [1.0] + [0.0] * 383
PREDICTION = ClassificationPrediction("bug", Priority.LOW, Priority.LOW, VECTOR)


class AuthorizationTests(ApiTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.reporter = await self.add_user("reporter@mail.com")
        self.other_reporter = await self.add_user("other@mail.com")
        self.other_staff = await self.add_user("other-staff@mail.com", "staff")
        self.reporter_headers = self.headers(self.reporter)

    async def report(self, user=None, *, vector=False):
        response = await self.client.post("/tickets/", json={"text": "Nie działa drukarka."},
                                          headers=self.headers(user or self.reporter))
        self.assertEqual(response.status_code, 201, response.text)
        ticket = response.json()["ticket"]
        if vector:
            with patch.object(self.runtime, "classifier", return_value=PREDICTION):
                await self.process(ticket["current_task_id"])
        return ticket

    async def transition(self, ticket_id, status, actor=None, **notes):
        return await self.client.patch(f"/tickets/{ticket_id}/status", json={"status": status, **notes},
                                       headers=self.headers(actor or self.user))

    async def assign(self, ticket_id, assignee=None):
        return await self.client.patch(f"/tickets/{ticket_id}/assignee",
                                       json={"assignee_id": (assignee or self.user).id}, headers=self.admin_headers)

    async def fail_classification(self, ticket):
        async with self.sessions() as db:
            task = await db.get(ClassificationTask, ticket["current_task_id"])
            task.state, task.error_code = "failed", "processing_failed"
            await db.commit()

    async def test_visibility_ownership_task_and_payload_spoofing(self):
        own = await self.report()
        other = await self.report(self.other_reporter)
        await self.add_ticket()
        for query in ["", "?status=reported", "?category=unknown&priority=medium", "?limit=1&offset=0"]:
            response = await self.client.get("/tickets/" + query, headers=self.reporter_headers)
            self.assertEqual([t["id"] for t in response.json()], [own["id"]])
        for suffix in ["", f"/task/{other['current_task_id']}"]:
            self.assertEqual((await self.client.get(f"/tickets/{other['id']}" + suffix, headers=self.reporter_headers)).status_code, 404)
        for actor in [self.user, self.admin]:
            self.assertEqual(len((await self.client.get("/tickets/", headers=self.headers(actor))).json()), 3)
            self.assertEqual((await self.client.get(f"/tickets/{other['id']}/task/{other['current_task_id']}", headers=self.headers(actor))).status_code, 200)
        for body in [{"text": "Opis", "author_id": self.admin.id}, {"text": "Opis", "assignee_id": self.user.id}]:
            self.assertEqual((await self.client.post("/tickets/", json=body, headers=self.reporter_headers)).status_code, 422)
        self.assertEqual(own["author_id"], self.reporter.id)
        self.assertIsNone(own["assignee_id"])

    async def test_edit_is_owner_only_and_immutable_after_acceptance_for_every_role(self):
        ticket = await self.report()
        path = f"/tickets/{ticket['id']}"
        for actor, code in [(self.other_reporter, 404), (self.user, 403), (self.admin, 403)]:
            response = await self.client.patch(path, json={"text": "Zmieniono opis"}, headers=self.headers(actor))
            self.assertEqual(response.status_code, code)
        response = await self.client.patch(path, json={"work_blocked": True}, headers=self.reporter_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ticket"]["priority"], "critical")
        self.assertEqual(response.json()["task_id"], ticket["current_task_id"])
        self.assertEqual((await self.assign(ticket["id"])).status_code, 200)
        for actor in [self.reporter, self.user, self.admin]:
            response = await self.client.patch(path, json={"text": "Nowy opis", "work_blocked": False}, headers=self.headers(actor))
            self.assertIn(response.status_code, [403, 409])
        # Również administrator będący autorem ma niezmienny opis po przyjęciu.
        for author in [self.user, self.admin]:
            own = await self.report(author)
            await self.assign(own["id"])
            response = await self.client.patch(f"/tickets/{own['id']}", json={"work_blocked": True}, headers=self.headers(author))
            self.assertEqual(response.status_code, 409)

    async def test_assignment_history_reassignment_and_current_handler(self):
        ticket = await self.report()
        accepted = await self.transition(ticket["id"], "accepted")
        self.assertEqual(accepted.status_code, 200)
        self.assertEqual(accepted.json()["assignee_id"], self.user.id)
        self.assertEqual(accepted.json()["author_id"], self.reporter.id)
        self.assertEqual(accepted.json()["status_changed_by_id"], self.user.id)
        self.assertEqual((await self.transition(ticket["id"], "accepted", self.other_staff)).status_code, 409)
        self.assertEqual((await self.transition(ticket["id"], "in_progress", self.other_staff)).status_code, 403)
        reassigned = await self.assign(ticket["id"], self.other_staff)
        self.assertEqual(reassigned.json()["status"], "accepted")
        self.assertEqual((await self.transition(ticket["id"], "in_progress")).status_code, 403)
        self.assertEqual((await self.transition(ticket["id"], "in_progress", self.other_staff)).status_code, 200)
        reassigned = await self.assign(ticket["id"])
        self.assertEqual(reassigned.json()["status"], "in_progress")
        self.assertEqual(reassigned.json()["current_task_id"], ticket["current_task_id"])
        self.assertEqual((await self.transition(ticket["id"], "resolved", self.other_staff, resolution_note="Naprawiono.")).status_code, 403)
        resolved = await self.transition(ticket["id"], "resolved", resolution_note="  Zainstalowano sterownik.  ")
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(resolved.json()["text"], ticket["text"])
        self.assertEqual(resolved.json()["resolution_note"], "Zainstalowano sterownik.")
        self.assertEqual(resolved.json()["resolved_by_id"], self.user.id)
        history = (await self.client.get(f"/tickets/{ticket['id']}/assignments")).json()
        self.assertEqual([(h["previous_assignee_id"], h["assignee_id"], h["changed_by_id"]) for h in history],
                         [(None, self.user.id, self.user.id), (self.user.id, self.other_staff.id, self.admin.id),
                          (self.other_staff.id, self.user.id, self.admin.id)])
        self.assertTrue(all(h["created_at"] for h in history))
        self.assertEqual((await self.assign(ticket["id"], self.other_staff)).status_code, 409)
        own_detail = (await self.client.get(f"/tickets/{ticket['id']}", headers=self.reporter_headers)).json()
        self.assertEqual(own_detail["resolution_note"], "Zainstalowano sterownik.")
        self.mock_delay.assert_called_once()

    async def test_assignment_targets_and_access(self):
        ticket = await self.report()
        inactive = await self.add_user("inactive@mail.com", "staff", active=False)
        pending = await self.add_user("pending@mail.com", approved=False)
        for target in [self.reporter, self.admin, inactive, pending]:
            self.assertEqual((await self.assign(ticket["id"], target)).status_code, 422)
        for actor in [self.reporter, self.user]:
            response = await self.client.patch(f"/tickets/{ticket['id']}/assignee", json={"assignee_id": self.user.id}, headers=self.headers(actor))
            self.assertEqual(response.status_code, 403)
        self.assertEqual((await self.transition(ticket["id"], "accepted", self.reporter)).status_code, 403)
        self.assertEqual((await self.transition(ticket["id"], "accepted", self.admin)).status_code, 403)
        self.assertEqual((await self.client.get(f"/tickets/{ticket['id']}/assignments", headers=self.reporter_headers)).status_code, 403)
        self.assertEqual((await self.assign(ticket["id"])).status_code, 200)

    async def test_cancellation_own_unassigned_only_and_terminal(self):
        ticket = await self.report(vector=True)
        for actor, expected in [(self.other_reporter, 404), (self.user, 403), (self.admin, 403)]:
            self.assertEqual((await self.transition(ticket["id"], "cancelled", actor)).status_code, expected)
        response = await self.transition(ticket["id"], "cancelled", self.reporter)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status_changed_by_id"], self.reporter.id)
        self.assertIsNotNone(response.json()["status_changed_at"])
        self.assertEqual((await self.transition(ticket["id"], "accepted")).status_code, 409)
        # Obrona także wobec dawnych/zaimportowanych rekordów reported z wykonawcą.
        another = await self.report()
        async with self.sessions() as db:
            stored = await db.get(Ticket, another["id"])
            stored.assignee_id = self.user.id
            await db.commit()
        self.assertEqual((await self.transition(another["id"], "cancelled", self.reporter)).status_code, 403)
        assigned = await self.report()
        await self.assign(assigned["id"])
        self.assertEqual((await self.transition(assigned["id"], "cancelled", self.reporter)).status_code, 409)

    async def test_rejection_matrix_notes_and_delete_cannot_bypass(self):
        for source in ["reported", "accepted", "in_progress"]:
            for actor in [self.reporter, self.user, self.other_staff, self.admin]:
                with self.subTest(source=source, role=actor.role, actor=actor.id):
                    ticket = await self.report()
                    if source != "reported":
                        await self.assign(ticket["id"])
                    if source == "in_progress":
                        await self.transition(ticket["id"], "in_progress")
                    expected = 200 if actor.role == "admin" or (actor.role == "staff" and source == "reported") else 403
                    response = await self.transition(ticket["id"], "rejected", actor, rejection_reason="  Powtórzona awaria.  ")
                    self.assertEqual(response.status_code, expected, response.text)
                    if expected == 200:
                        self.assertEqual(response.json()["rejected_by_id"], actor.id)
                        detail = (await self.client.get(f"/tickets/{ticket['id']}", headers=self.reporter_headers)).json()
                        self.assertEqual(detail["rejection_reason"], "Powtórzona awaria.")
                        self.assertIsNotNone(detail["rejected_at"])
                    else:
                        alias = await self.client.request("DELETE", f"/tickets/{ticket['id']}",
                                                          json={"status": "rejected", "rejection_reason": "Powód"}, headers=self.headers(actor))
                        self.assertEqual(alias.status_code, 403)
        self.assertEqual(self.mock_delay.call_count, 12)

    async def test_resolution_requires_sequence_and_current_assignee_including_admin(self):
        ticket = await self.report()
        for source in ["reported", "accepted", "in_progress"]:
            if source == "accepted":
                await self.assign(ticket["id"])
            if source == "in_progress":
                await self.transition(ticket["id"], "in_progress")
            for actor in [self.reporter, self.other_staff, self.user, self.admin]:
                if source != "in_progress":
                    result = await self.transition(ticket["id"], "resolved", actor, resolution_note="Naprawiono")
                    self.assertEqual(result.status_code, 409)
                else:
                    back = await self.transition(ticket["id"], "accepted", actor)
                    self.assertEqual(back.status_code, 409)
            if source == "in_progress":
                for actor in [self.reporter, self.other_staff]:
                    self.assertEqual((await self.transition(ticket["id"], "resolved", actor, resolution_note="Naprawiono")).status_code, 403)
                for note in [None, " \t "]:
                    self.assertEqual((await self.transition(ticket["id"], "resolved", self.admin, resolution_note=note)).status_code, 422)
                resolved = await self.transition(ticket["id"], "resolved", self.admin, resolution_note="Naprawiono")
                self.assertEqual(resolved.status_code, 200)
                self.assertEqual(resolved.json()["resolved_by_id"], self.admin.id)

    async def test_retry_matrix_and_previous_handler(self):
        for source in ["reported", "accepted", "in_progress", "resolved", "rejected", "cancelled"]:
            for actor in [self.reporter, self.user, self.other_staff, self.admin]:
                ticket = await self.report()
                await self.fail_classification(ticket)
                async with self.sessions() as db:
                    stored = await db.get(Ticket, ticket["id"])
                    stored.status = source
                    stored.assignee_id = self.user.id if source in ("accepted", "in_progress") else None
                    await db.commit()
                response = await self.client.post(f"/tickets/{ticket['id']}/classification/retry", headers=self.headers(actor))
                allowed = source in ("reported", "accepted", "in_progress") and (
                    actor.role == "admin" or (source == "reported" and actor.id == self.reporter.id)
                    or (source in ("accepted", "in_progress") and actor.id == self.user.id))
                expected = 202 if allowed else (409 if source in ("resolved", "rejected", "cancelled") else 403)
                self.assertEqual(response.status_code, expected, response.text)
        ticket = await self.report()
        await self.fail_classification(ticket)
        await self.assign(ticket["id"])
        await self.assign(ticket["id"], self.other_staff)
        self.assertEqual((await self.client.post(f"/tickets/{ticket['id']}/classification/retry")).status_code, 403)

    async def test_manual_priority_admin_only_survives_processing_and_checkbox(self):
        ticket = await self.report()
        url = f"/tickets/{ticket['id']}/priority"
        for actor in [self.reporter, self.user]:
            self.assertEqual((await self.client.patch(url, json={"priority": "low"}, headers=self.headers(actor))).status_code, 403)
        response = await self.client.patch(url, json={"priority": "low"}, headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["manual_priority_by_id"], self.admin.id)
        with patch.object(self.runtime, "classifier", return_value=PREDICTION):
            await self.process(ticket["current_task_id"])
        response = await self.client.patch(f"/tickets/{ticket['id']}", json={"work_blocked": True}, headers=self.reporter_headers)
        self.assertEqual(response.json()["ticket"]["priority"], "low")
        self.assertEqual(response.json()["ticket"]["priority_source"], "administrator")

    async def test_duplicate_query_and_delete_alias_filter_visibility(self):
        own = await self.report(vector=True)
        another = await self.report(vector=True)
        await self.report(self.other_reporter, vector=True)
        async with self.sessions() as db:
            rows = await find_similar_open_tickets(own["id"], VECTOR, "bug", db, actor=self.reporter)
            self.assertEqual([r["id"] for r in rows], [another["id"]])
            rows = await find_similar_open_tickets(own["id"], VECTOR, "bug", db, actor=self.user)
            self.assertEqual(len(rows), 2)
        response = await self.client.request("DELETE", f"/tickets/{own['id']}", json={"status": "cancelled"}, headers=self.reporter_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([r["id"] for r in response.json()["suggested_duplicates"]], [another["id"]])

    async def test_concurrent_accept_cancel_assign_reject_and_resolve(self):
        for competing in ["accept", "assign", "reject"]:
            ticket = await self.report()
            cancellation = self.transition(ticket["id"], "cancelled", self.reporter)
            competitor = (self.assign(ticket["id"]) if competing == "assign" else
                          self.transition(ticket["id"], "accepted") if competing == "accept" else
                          self.transition(ticket["id"], "rejected", rejection_reason="Duplikat"))
            responses = await asyncio.gather(cancellation, competitor)
            self.assertEqual(sorted(r.status_code for r in responses), [200, 409])
            detail = (await self.client.get(f"/tickets/{ticket['id']}")).json()
            if detail["status"] == "cancelled":
                self.assertIsNone(detail["assignee_id"])
        # Dwóch wykonawców przyjmuje jednocześnie; historia ma tylko jednego zwycięzcę.
        ticket = await self.report()
        responses = await asyncio.gather(self.transition(ticket["id"], "accepted"), self.transition(ticket["id"], "accepted", self.other_staff))
        self.assertEqual(sorted(r.status_code for r in responses), [200, 409])
        history = (await self.client.get(f"/tickets/{ticket['id']}/assignments")).json()
        self.assertEqual(len(history), 1)
        winner = next(r.json() for r in responses if r.status_code == 200)
        self.assertEqual(history[0]["assignee_id"], winner["assignee_id"])
        for competitor in ["accept", "resolve"]:
            ticket = await self.report()
            if competitor == "resolve":
                await self.assign(ticket["id"])
                await self.transition(ticket["id"], "in_progress")
            other = (self.transition(ticket["id"], "accepted") if competitor == "accept" else
                     self.transition(ticket["id"], "resolved", resolution_note="Naprawiono"))
            results = await asyncio.gather(other, self.transition(ticket["id"], "rejected", self.admin, rejection_reason="Duplikat"))
            codes = sorted(r.status_code for r in results)
            self.assertIn(codes, [[200, 409], [200, 200]] if competitor == "accept" else [[200, 409]])
            # Dwie sekwencyjne poprawne decyzje accepted -> rejected są dozwolone administratorowi.
            self.assertEqual((await self.client.get(f"/tickets/{ticket['id']}")).json()["status"], "resolved" if competitor == "resolve" and results[0].status_code == 200 else "rejected")

    async def test_late_classification_cannot_undo_cancellation(self):
        ticket = await self.report()
        entered, release = asyncio.Event(), asyncio.Event()
        async def delayed(*args):
            entered.set()
            await release.wait()
            return PREDICTION
        with patch.object(self.runtime, "classifier", side_effect=delayed):
            processing = asyncio.create_task(self.process(ticket["current_task_id"]))
            try:
                await asyncio.wait_for(entered.wait(), 3)
                self.assertEqual((await self.transition(ticket["id"], "cancelled", self.reporter)).status_code, 200)
            finally:
                release.set()
                await processing
        actual = (await self.client.get(f"/tickets/{ticket['id']}", headers=self.reporter_headers)).json()
        self.assertEqual(actual["status"], "cancelled")
        self.assertFalse(actual["classification_current"])

    async def test_legacy_import_is_explicit_atomic_and_cannot_overwrite(self):
        async with self.sessions() as db:
            legacy = Ticket(text="Stary opis", category="bug", priority="medium", legacy_unowned=True)
            db.add(legacy)
            await db.commit()
            ticket_id = legacy.id
        self.assertEqual((await self.client.get(f"/tickets/{ticket_id}", headers=self.reporter_headers)).status_code, 404)
        async with self.sessions() as db:
            with self.assertRaises(InvalidInputError):
                await import_authors(db, {str(ticket_id): self.reporter.email, "999999": self.reporter.email})
        async with self.sessions() as db:
            self.assertIsNone((await db.get(Ticket, ticket_id)).author_id)
            self.assertEqual(await import_authors(db, {str(ticket_id): self.reporter.email}), 1)
        response = await self.client.get(f"/tickets/{ticket_id}", headers=self.reporter_headers)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["legacy_unowned"])
        async with self.sessions() as db:
            with self.assertRaises(InvalidInputError):
                await import_authors(db, {str(ticket_id): self.other_reporter.email})
        async with self.sessions() as db:
            db.add(Ticket(text="Bez autora", category="bug", priority="medium"))
            with self.assertRaises(IntegrityError):
                await db.commit()
