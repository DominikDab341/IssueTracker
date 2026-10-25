"""Diagnostyka błędów bez danych zgłoszenia i parametrów SQL w logach."""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.exc import StatementError

from app.services.processing import ProcessingRuntime


LOGGER = "app.services.processing"


class ProcessingDiagnosticsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Konfiguracja logów Alembic z wcześniejszych testów może wyłączyć logger.
        logger_patch = patch("app.services.processing.logger.disabled", False)
        logger_patch.start()
        self.addCleanup(logger_patch.stop)

    async def test_failure_stage_and_stack_are_logged_without_exception_payload(self):
        for stage in ["claim", "classify", "save_result"]:
            with self.subTest(stage=stage):
                classifier = AsyncMock()
                runtime = ProcessingRuntime(MagicMock(), classifier=classifier)
                runtime._claim = AsyncMock(return_value="PRIVATE_TICKET_TEXT")
                runtime._save_result = AsyncMock()
                runtime._record_failure = AsyncMock()

                async def fail(*args, **kwargs):
                    raise StatementError(
                        "PRIVATE_EXCEPTION_MESSAGE", "PRIVATE_SQL_STATEMENT",
                        {"text": "PRIVATE_TICKET_TEXT", "password": "PRIVATE_PASSWORD"},
                        RuntimeError("PRIVATE_ORIGINAL_EXCEPTION"),
                    )

                if stage == "claim":
                    runtime._claim.side_effect = fail
                elif stage == "classify":
                    classifier.side_effect = fail
                else:
                    runtime._save_result.side_effect = fail

                with self.assertLogs(LOGGER, level="ERROR") as captured:
                    await runtime.process("task-probe")
                output = "\n".join(captured.output)
                self.assertIn("task-probe", output)
                self.assertIn(f"stage={stage}", output)
                self.assertIn("error_type=StatementError", output)
                self.assertIn("test_processing_diagnostics.py", output)
                self.assertIn("in fail", output)
                self.assertNotIn("PRIVATE_", output)
                runtime._record_failure.assert_awaited_once_with("task-probe")

    async def test_failure_to_record_error_also_has_safe_diagnostics(self):
        def unavailable_session():
            raise RuntimeError("PRIVATE_DATABASE_CREDENTIALS")

        runtime = ProcessingRuntime(unavailable_session, classifier=AsyncMock())
        with self.assertLogs(LOGGER, level="ERROR") as captured:
            await runtime._record_failure("task-probe")
        output = "\n".join(captured.output)
        self.assertIn("stage=record_failure", output)
        self.assertIn("error_type=RuntimeError", output)
        self.assertIn("in unavailable_session", output)
        self.assertIn("potrzebna kontrola po restarcie", output)
        self.assertNotIn("PRIVATE_", output)
