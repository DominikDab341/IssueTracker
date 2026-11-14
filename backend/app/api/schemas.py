from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator, model_validator

from app.domain import Category, Priority, TaskState
from app.services.text_validation import normalize_ticket_text
from app.ticket_status import (
    MAX_STATUS_NOTE_LENGTH, TicketStatus, normalize_status_note, validate_status_notes,
)


class TicketStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: TicketStatus
    resolution_note: str | None = Field(default=None, max_length=MAX_STATUS_NOTE_LENGTH)
    rejection_reason: str | None = Field(default=None, max_length=MAX_STATUS_NOTE_LENGTH)

    @field_validator("resolution_note", "rejection_reason")
    @classmethod
    def nonempty_note(cls, value):
        return normalize_status_note(value)

    @model_validator(mode="after")
    def require_notes(self):
        validate_status_notes(self.status, self.resolution_note, self.rejection_reason)
        return self


class TicketCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str
    work_blocked: StrictBool = False

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return normalize_ticket_text(value)


class TicketEdit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str | None = None
    work_blocked: StrictBool | None = None

    @field_validator("text", "work_blocked")
    @classmethod
    def nonnull(cls, value):
        if value is None:
            raise ValueError("This field cannot be null.")
        return value

    @field_validator("text")
    @classmethod
    def validate_text(cls, value):
        return normalize_ticket_text(value)

    @model_validator(mode="after")
    def not_empty(self):
        if not self.model_fields_set:
            raise ValueError("Podaj opis lub pole blokady pracy.")
        return self


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int | None
    assignee_id: int | None
    legacy_unowned: bool
    status_changed_by_id: int | None
    status_changed_at: datetime | None
    resolved_by_id: int | None
    rejected_by_id: int | None
    manual_priority_by_id: int | None
    manual_priority_at: datetime | None
    text: str
    category: str
    legacy_category: str | None
    classification_version: str | None
    predicted_category: str | None
    predicted_category_version: int | None
    manual_category: str | None
    manual_category_version: int | None
    manual_category_by_id: int | None
    manual_category_at: datetime | None
    manual_category_current: bool
    priority: str
    created_at: datetime
    updated_at: datetime
    status: TicketStatus
    resolution_note: str | None
    rejection_reason: str | None
    resolved_at: datetime | None
    rejected_at: datetime | None
    work_blocked: bool
    content_version: int
    embedding_version: int | None
    classification_current: bool
    needs_review: bool
    priority_needs_review: bool
    predicted_base_priority: str | None
    category_score: float | None
    priority_score: float | None
    category_review_reason: str | None
    priority_review_reason: str | None
    review_version: int | None
    escalation_min_priority: str | None
    escalated_at: datetime | None
    escalation_reason: str | None
    current_task_state: TaskState | None = None
    current_task_id: str | None
    base_priority: str | None
    priority_source: str


class TicketCreateResponse(BaseModel):
    """Identyfikator zadania zapisanego razem ze zgłoszeniem w PostgreSQL."""
    ticket: TicketResponse
    task_id: str


class ClassificationResultResponse(BaseModel):
    category: str
    base_priority: Priority | None
    automatic_priority: Priority | None
    classification_version: str | None = None
    accepted_category: str | None = None
    predicted_base_priority: Priority | None = None
    category_score: float | None = None
    priority_score: float | None = None
    category_review_reason: str | None = None
    priority_review_reason: str | None = None


class TaskStatusResponse(BaseModel):
    task_id: str
    state: TaskState
    content_version: int
    current: bool
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    result: ClassificationResultResponse | None = None
    error: str | None = None
    error_code: str | None = None


class TicketEditResponse(BaseModel):
    ticket: TicketResponse
    task_id: str | None


class SuggestedDuplicate(BaseModel):
    id: int
    text: str
    similarity: float


class TicketCloseResponse(BaseModel):
    ticket: TicketResponse
    status: Literal[TicketStatus.RESOLVED, TicketStatus.REJECTED, TicketStatus.CANCELLED]
    suggested_duplicates: list[SuggestedDuplicate] = Field(default_factory=list)


class AssignmentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    assignee_id: int = Field(gt=0, strict=True)


class PriorityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    priority: Priority


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Category
    expected_content_version: int = Field(gt=0, strict=True)


class ReferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: str
    base_priority: str
    source_ticket_id: int
    source_content_version: int
    approved_by_id: int
    approved_at: datetime


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ticket_id: int
    previous_assignee_id: int | None
    assignee_id: int
    changed_by_id: int
    created_at: datetime
