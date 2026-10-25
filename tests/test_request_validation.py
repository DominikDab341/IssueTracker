"""Walidacja HTTP bez bazy i pobierania modelu."""
import asyncio
from threading import Event, get_ident
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from app.api.main import app
from app.api.dependencies import get_processing_runtime
from app.database.database import get_db
from app.services.text_validation import TokenizerUnavailableError


class RequestValidationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        async def database_override():
            yield SimpleNamespace()  # Próba SQL zakończy test błędem.

        async def runtime_override():
            return SimpleNamespace(run_id="request-validation")

        app.dependency_overrides[get_db] = database_override
        app.dependency_overrides[get_processing_runtime] = runtime_override
        self.client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()
        app.dependency_overrides.clear()

    async def test_slow_tokenizer_does_not_block_other_http_requests(self):
        for method, path in [("POST", "/tickets/"), ("PATCH", "/tickets/1")]:
            with self.subTest(method=method):
                entered, release = asyncio.Event(), Event()
                loop = asyncio.get_running_loop()
                event_loop_thread = get_ident()
                worker_threads = []

                def encode(*args, **kwargs):
                    worker_threads.append(get_ident())
                    loop.call_soon_threadsafe(entered.set)
                    if not release.wait(5):
                        raise RuntimeError("Test nie zwolnił tokenizera.")
                    return [1] * 257

                with patch("app.services.text_validation.get_tokenizer",
                           return_value=SimpleNamespace(encode=encode)):
                    request = asyncio.create_task(self.client.request(method, path, json={"text": "Opis."}))
                    try:
                        await asyncio.wait_for(entered.wait(), 2)
                        self.assertNotIn(event_loop_thread, worker_threads)
                        self.assertFalse(request.done())
                        other = await asyncio.wait_for(self.client.get("/openapi.json"), 2)
                        self.assertEqual(other.status_code, 200)
                        self.assertFalse(request.done())
                    finally:
                        release.set()
                        response = await request
                self.assertEqual(response.status_code, 422)
                error = response.json()["detail"][0]
                self.assertEqual(error["loc"], ["body", "text"])
                self.assertIn("257", error["msg"])

    async def test_tokenizer_unavailable_remains_503_before_database_access(self):
        for method, path in [("POST", "/tickets/"), ("PATCH", "/tickets/1")]:
            with self.subTest(method=method):
                with patch("app.services.text_validation.get_tokenizer",
                           side_effect=TokenizerUnavailableError("Tokenizer jest niedostępny.")):
                    response = await self.client.request(method, path, json={"text": "Opis."})
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json()["detail"], "Tokenizer jest niedostępny.")

    async def test_invalid_text_is_rejected_without_loading_tokenizer(self):
        with patch("app.services.text_validation.get_tokenizer") as tokenizer:
            for method, path in [("POST", "/tickets/"), ("PATCH", "/tickets/1")]:
                for description in [" \n\t ", "x" * 10001]:
                    response = await self.client.request(method, path, json={"text": description})
                    self.assertEqual(response.status_code, 422)
            tokenizer.assert_not_called()
