import asyncio
import os
import socket
import subprocess
import sys
import time
import unittest

from alembic import command
import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from tests.support import TEST_URL, ROOT, migration_config


class ProcessRestartTests(unittest.TestCase):
    def test_http_response_before_completion_process_kill_restart_and_retry(self):
        command.upgrade(migration_config(), "head")

        async def clear():
            engine = create_async_engine(TEST_URL)
            async with engine.begin() as connection:
                await connection.execute(text("TRUNCATE classification_tasks, tickets RESTART IDENTITY"))
            await engine.dispose()

        asyncio.run(clear())
        with socket.socket() as port_socket:
            port_socket.bind(("127.0.0.1", 0))
            port = port_socket.getsockname()[1]
        client = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=3)
        processes = []

        def start(mode):
            process = subprocess.Popen(
                [sys.executable, "-m", "tests.background_server", str(port), mode], cwd=ROOT,
                env=os.environ.copy(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            processes.append(process)
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    self.fail(f"Testowy proces API zakończył się kodem {process.returncode}.")
                try:
                    if client.get("/tickets/").status_code == 200:
                        return process
                except httpx.TransportError:
                    pass
                time.sleep(.1)
            self.fail("Testowy proces API nie wystartował w 45 s.")

        def wait_state(path, expected):
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                response = client.get(path)
                self.assertEqual(response.status_code, 200)
                state = response.json()
                if state["state"] == expected:
                    return state
                time.sleep(.05)
            self.fail(f"Brak stanu {expected}.")

        try:
            process = start("slow")
            response = client.post("/tickets/", json={"text": "Nie działa sieć.", "work_blocked": True})
            self.assertEqual(response.status_code, 201, response.text)
            ticket = response.json()["ticket"]
            path = f"/tickets/{ticket['id']}/task/{ticket['current_task_id']}"
            wait_state(path, "running")
            # A second HTTP request works while the 120-second encoder is still running.
            self.assertEqual(client.get(f"/tickets/{ticket['id']}").json()["priority"], "critical")
            process.kill()
            process.wait(timeout=10)
            client.close()
            client = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=3)
            start("fast")
            interrupted = wait_state(path, "failed")
            self.assertEqual(interrupted["error_code"], "interrupted")
            self.assertEqual(client.get(f"/tickets/{ticket['id']}").json()["text"], "Nie działa sieć.")
            retry = client.post(f"/tickets/{ticket['id']}/classification/retry")
            self.assertEqual(retry.status_code, 202, retry.text)
            task_id = retry.json()["task_id"]
            self.assertNotEqual(task_id, ticket["current_task_id"])
            wait_state(f"/tickets/{ticket['id']}/task/{task_id}", "succeeded")
            result = client.get(f"/tickets/{ticket['id']}").json()
            self.assertTrue(result["classification_current"])
            self.assertEqual(result["priority"], "critical")
            self.assertEqual(result["status"], "reported")
        finally:
            client.close()
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=10)
