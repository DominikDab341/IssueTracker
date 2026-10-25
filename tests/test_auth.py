import asyncio
from datetime import timedelta
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
import jwt
from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError

from tests.test_api import ApiTestCase, TEST_PASSWORD, setUpModule
from app.api.main import app
from app.api.dependencies import get_assistant_user
from app.database.database import get_db
from app.models.models import User, Ticket
from app.services.auth import jwt_secret, password_hasher
from app.services.errors import ConflictError
from app.services.tasks import now
from app.services.users import UserService


class AuthenticationTests(ApiTestCase):
    async def register(self, email="nowy@mail.com", **extra):
        return await self.client.post("/auth/register", json={"email": email, "password": TEST_PASSWORD, **extra})

    async def login(self, email="nowy@mail.com", password=TEST_PASSWORD):
        return await self.client.post("/auth/token", data={"username": email, "password": password})

    async def test_registration_domain_normalization_and_no_role_escalation(self):
        response = await self.register("NOWY@MAIL.COM")
        self.assertEqual(response.status_code, 201, response.text)
        user = response.json()
        self.assertEqual(user["email"], "nowy@mail.com")
        self.assertIsNone(user["role"])
        self.assertFalse(user["is_approved"])
        self.assertTrue(user["is_active"])
        self.assertIsNone(user["approved_at"])
        self.assertIsNone(user["approved_by_id"])
        self.assertNotIn("password", response.text)
        async with self.sessions() as db:
            stored = await db.get(User, user["id"])
            self.assertTrue(stored.password_hash.startswith("$argon2id$"))
            self.assertTrue(password_hasher.verify(TEST_PASSWORD, stored.password_hash))
        self.assertEqual((await self.register("Nowy@mail.com")).status_code, 409)
        for email in ["wrong@example.com", "bad@evilmail.com", "bad@mail.com.evil.org", "bad@sub.mail.com", "nie-email"]:
            self.assertEqual((await self.register(email)).status_code, 422, email)
        for extra in [{"role": "admin"}, {"is_approved": True}, {"is_active": True}, {"approved_by_id": self.admin.id}]:
            self.assertEqual((await self.register("attack@mail.com", **extra)).status_code, 422)
        for password in ["weak!", "x" * 129]:
            result = await self.client.post("/auth/register", json={"email": "bad@mail.com", "password": password})
            self.assertEqual(result.status_code, 422)
            self.assertNotIn(password, result.text)

    async def test_pending_approval_login_deactivation_and_role_are_live(self):
        user = (await self.register()).json()
        self.assertEqual((await self.login()).status_code, 403)
        signed_pending = self.headers(type("UserId", (), {"id": user["id"]})())
        self.assertEqual((await self.client.get("/users/me", headers=signed_pending)).status_code, 403)
        approved = await self.client.post(f"/admin/users/{user['id']}/approve", json={"role": "reporter"}, headers=self.admin_headers)
        self.assertEqual(approved.status_code, 200)
        self.assertEqual(approved.json()["approved_by_id"], self.admin.id)
        token = await self.login("NOWY@MAIL.COM")
        self.assertEqual(token.status_code, 200)
        self.assertEqual(token.json()["expires_in"], 1800)
        self.assertEqual(token.headers["cache-control"], "no-store")
        headers = {"Authorization": "Bearer " + token.json()["access_token"]}
        self.assertEqual((await self.client.get("/users/me", headers=headers)).json()["role"], "reporter")
        await self.client.patch(f"/admin/users/{user['id']}/role", json={"role": "staff"}, headers=self.admin_headers)
        self.assertEqual((await self.client.get("/users/me", headers=headers)).json()["role"], "staff")
        await self.client.patch(f"/admin/users/{user['id']}/active", json={"is_active": False}, headers=self.admin_headers)
        self.assertEqual((await self.client.get("/tickets/", headers=headers)).status_code, 403)
        self.assertEqual((await self.login()).status_code, 403)
        state = (await self.client.get("/admin/users?pending=false", headers=self.admin_headers)).json()
        saved = next(u for u in state if u["id"] == user["id"])
        self.assertTrue(saved["is_approved"])
        self.assertFalse(saved["is_active"])
        await self.client.patch(f"/admin/users/{user['id']}/active", json={"is_active": True}, headers=self.admin_headers)
        self.assertEqual((await self.login()).status_code, 200)

    async def test_bad_password_invalid_expired_and_missing_tokens(self):
        for email, password in [(self.user.email, "bad-password"), ("missing@mail.com", TEST_PASSWORD), (self.user.email, "x" * 129)]:
            response = await self.login(email, password)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.headers["www-authenticate"], "Bearer")
        claims = {"sub": str(self.user.id), "iat": now() - timedelta(hours=1), "exp": now() - timedelta(minutes=1),
                  "iss": "issuetracker", "aud": "issuetracker-api"}
        expired = jwt.encode(claims, jwt_secret(), algorithm="HS256")
        missing_exp = jwt.encode({k: v for k, v in claims.items() if k != "exp"}, jwt_secret(), algorithm="HS256")
        wrong_key = jwt.encode({**claims, "exp": now() + timedelta(minutes=5)}, "wrong-signing-key-for-test-at-least-32-bytes", algorithm="HS256")
        wrong_audience = jwt.encode({**claims, "exp": now() + timedelta(minutes=5), "aud": "other-app"}, jwt_secret(), algorithm="HS256")
        for token in ["", "broken", expired, missing_exp, wrong_key, wrong_audience]:
            response = await self.client.get("/users/me", headers={"Authorization": "Bearer " + token})
            self.assertEqual(response.status_code, 401)
        self.client.headers.pop("Authorization")
        for method, path, payload in [("GET", "/tickets/", None), ("GET", "/tickets/1", None),
                                       ("GET", "/tickets/1/task/id", None), ("POST", "/tickets/", {"text": "Opis"}),
                                       ("PATCH", "/tickets/1", {"work_blocked": True}),
                                       ("PATCH", "/tickets/1/status", {"status": "cancelled"}),
                                       ("DELETE", "/tickets/1", {"status": "cancelled"}),
                                       ("PATCH", "/tickets/1/priority", {"priority": "low"}),
                                       ("PATCH", "/tickets/1/category", {"category": "bug"}),
                                       ("PATCH", "/tickets/1/assignee", {"assignee_id": 1}),
                                       ("GET", "/tickets/1/assignments", None),
                                       ("POST", "/tickets/1/classification/retry", None),
                                       ("GET", "/admin/users", None)]:
            self.assertEqual((await self.client.request(method, path, json=payload)).status_code, 401, path)

    async def test_approval_validation_atomicity_and_race(self):
        user = (await self.register()).json()
        url = f"/admin/users/{user['id']}/approve"
        for body in [{}, {"role": None}, {"role": "superuser"}]:
            self.assertEqual((await self.client.post(url, json=body, headers=self.admin_headers)).status_code, 422)
        self.assertEqual((await self.client.post(url, json={"role": "admin"})).status_code, 403)
        self.assertEqual((await self.client.patch(f"/admin/users/{user['id']}/role", json={"role": "staff"}, headers=self.admin_headers)).status_code, 409)
        pending = (await self.client.get("/admin/users?pending=true", headers=self.admin_headers)).json()
        self.assertEqual([u["id"] for u in pending], [user["id"]])
        self.assertIsNone(pending[0]["role"])
        results = await asyncio.gather(*[
            self.client.post(url, json={"role": role}, headers=self.admin_headers) for role in ("reporter", "staff")
        ])
        self.assertEqual(sorted(r.status_code for r in results), [200, 409])
        accepted = next(r.json() for r in results if r.status_code == 200)
        async with self.sessions() as db:
            actual = await db.get(User, user["id"])
            self.assertEqual(actual.role, accepted["role"])
            self.assertEqual(actual.approved_by_id, self.admin.id)
            self.assertIsNotNone(actual.approved_at)

    async def test_administration_forbidden_to_staff_and_reporter(self):
        reporter = await self.add_user("reporter@mail.com")
        pending = (await self.register()).json()
        for actor in [self.user, reporter]:
            for method, path, body in [
                ("GET", "/admin/users", None),
                ("POST", f"/admin/users/{pending['id']}/approve", {"role": "admin"}),
                ("PATCH", f"/admin/users/{self.user.id}/role", {"role": "admin"}),
                ("PATCH", f"/admin/users/{self.admin.id}/active", {"is_active": False}),
            ]:
                response = await self.client.request(method, path, json=body, headers=self.headers(actor))
                self.assertEqual(response.status_code, 403)
        for query in ["limit=0", "limit=101", "offset=-1"]:
            self.assertEqual((await self.client.get("/admin/users?" + query, headers=self.admin_headers)).status_code, 422)

    async def test_assistant_guard_all_roles_and_live_role_change(self):
        # Endpoint LLM powstanie w etapie 7; ten sam dependency jest gotowy do jego użycia.
        probe = FastAPI()
        probe.exception_handlers.update(app.exception_handlers)
        probe.dependency_overrides[get_db] = app.dependency_overrides[get_db]

        @probe.get("/assistant-probe")
        async def assistant(user=Depends(get_assistant_user)):
            return {"id": user.id}

        reporter = await self.add_user("reporter@mail.com")
        async with AsyncClient(transport=ASGITransport(app=probe), base_url="http://test") as client:
            self.assertEqual((await client.get("/assistant-probe")).status_code, 401)
            for user, expected in [(reporter, 403), (self.user, 200), (self.admin, 200)]:
                self.assertEqual((await client.get("/assistant-probe", headers=self.headers(user))).status_code, expected)
            old_staff_token = self.headers(self.user)
            await self.client.patch(f"/admin/users/{self.user.id}/role", json={"role": "reporter"}, headers=self.admin_headers)
            self.assertEqual((await client.get("/assistant-probe", headers=old_staff_token)).status_code, 403)

    async def test_bootstrap_is_once_no_overwrite_and_serialized(self):
        async with self.sessions() as db:
            await db.execute(delete(User))
            await db.commit()
        async def bootstrap(email):
            async with self.sessions() as db:
                try:
                    return await UserService(db).bootstrap_admin(email, TEST_PASSWORD)
                except ConflictError as exc:
                    return exc
        results = await asyncio.gather(bootstrap("first@mail.com"), bootstrap("second@mail.com"))
        self.assertEqual(sum(isinstance(r, User) for r in results), 1)
        winner = next(r for r in results if isinstance(r, User))
        self.assertEqual(winner.role, "admin")
        self.assertTrue(winner.is_active and winner.is_approved)
        self.assertTrue(password_hasher.verify(TEST_PASSWORD, winner.password_hash))
        async with self.sessions() as db:
            await db.execute(delete(User))
            await db.commit()
        existing = await self.add_user("existing@mail.com", approved=False)
        result = await bootstrap(existing.email)
        self.assertIsInstance(result, ConflictError)
        async with self.sessions() as db:
            actual = await db.get(User, existing.id)
            self.assertFalse(actual.is_approved)
            self.assertIsNone(actual.role)

    async def test_database_rejects_approved_account_without_role(self):
        async with self.sessions() as db:
            db.add(User(email="invalid@mail.com", password_hash="unused", is_approved=True, approved_at=now()))
            with self.assertRaises(IntegrityError):
                await db.commit()


class BootstrapCommandTests(unittest.TestCase):
    def test_command_refuses_terminal_without_hidden_password_input(self):
        from getpass import GetPassWarning
        from scripts import create_admin
        with patch("sys.argv", ["create_admin.py", "--email", "first@mail.com"]), \
                patch.object(create_admin, "getpass", side_effect=GetPassWarning()), \
                patch.object(create_admin, "create", new_callable=AsyncMock) as create, patch("sys.stderr"):
            with self.assertRaises(SystemExit) as error:
                create_admin.main()
        self.assertEqual(error.exception.code, 1)
        create.assert_not_called()

    def test_password_is_prompted_without_command_argument_or_output(self):
        from scripts import create_admin
        with patch("sys.argv", ["create_admin.py", "--email", "first@mail.com"]), \
                patch.object(create_admin, "getpass", return_value="test-bootstrap-password") as prompt, \
                patch.object(create_admin, "create", new_callable=AsyncMock) as create, patch("builtins.print") as output:
            create_admin.main()
        self.assertEqual(prompt.call_count, 2)
        create.assert_awaited_once_with("first@mail.com", "test-bootstrap-password")
        self.assertNotIn("test-bootstrap-password", str(output.call_args_list))
