"""Wspólne typy biznesowe, niezależne od HTTP i bazy danych."""
from dataclasses import dataclass
from enum import StrEnum


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PrioritySource(StrEnum):
    LEGACY = "legacy"
    ADMINISTRATOR = "administrator"
    WORK_BLOCKED = "work_blocked"
    AUTOMATIC = "automatic"
    FALLBACK = "fallback"


class TaskState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TaskErrorCode(StrEnum):
    PROCESSING_FAILED = "processing_failed"
    INTERRUPTED = "interrupted"
    OBSOLETE = "obsolete"
    SUPERSEDED = "superseded"


PRIORITIES = frozenset(Priority)
ACTIVE_TASK_STATES = (TaskState.PENDING, TaskState.RUNNING)
RETRYABLE_ERRORS = frozenset((TaskErrorCode.PROCESSING_FAILED, TaskErrorCode.INTERRUPTED))


@dataclass(frozen=True)
class ClassificationPrediction:
    category: str
    base_priority: Priority | None
    automatic_priority: Priority | None
    vector: list[float]
