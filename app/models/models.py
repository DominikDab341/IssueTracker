from datetime import datetime
from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, DateTime, func, CheckConstraint, UniqueConstraint, text as sql_text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base
from pgvector.sqlalchemy import Vector
from app.domain import PrioritySource, TaskState
from app.ticket_status import TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(
            "status IN ('reported', 'accepted', 'in_progress', 'resolved', 'rejected', 'cancelled')",
            name="ck_ticket_status"
        ),
        CheckConstraint("author_id IS NOT NULL OR legacy_unowned", name="ck_ticket_author"),
        CheckConstraint("manual_category IS NULL OR manual_category IN ('bug', 'performance', 'feature')",
                        name="ck_ticket_manual_category"),
        CheckConstraint("(manual_category IS NULL AND manual_category_version IS NULL AND "
                        "manual_category_by_id IS NULL AND manual_category_at IS NULL) OR "
                        "(manual_category IS NOT NULL AND manual_category_version IS NOT NULL AND "
                        "manual_category_by_id IS NOT NULL AND manual_category_at IS NOT NULL AND "
                        "manual_category_version > 0 AND manual_category_version <= content_version)",
                        name="ck_ticket_manual_category_metadata"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    legacy_unowned: Mapped[bool] = mapped_column(Boolean, default=False, server_default=sql_text("false"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    status_changed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    rejected_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    manual_priority_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    manual_priority_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    text: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    predicted_category: Mapped[str | None] = mapped_column(String(50))
    predicted_category_version: Mapped[int | None] = mapped_column(Integer)
    manual_category: Mapped[str | None] = mapped_column(String(50))
    manual_category_version: Mapped[int | None] = mapped_column(Integer)
    manual_category_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    manual_category_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=TicketStatus.REPORTED, server_default="reported")
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    work_blocked: Mapped[bool] = mapped_column(Boolean, default=False, server_default=sql_text("false"))
    content_version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    embedding_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    base_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    automatic_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Pole chronione przed zmianą przez formularz i klasyfikację.
    manual_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    priority_source: Mapped[str] = mapped_column(String(30), default=PrioritySource.LEGACY, server_default="legacy")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    embedding_vector: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)

    @property
    def classification_current(self) -> bool:
        return self.embedding_version is not None and self.embedding_version == self.content_version

    @property
    def manual_category_current(self) -> bool:
        return self.manual_category is not None and self.manual_category_version == self.content_version


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IS NULL OR role IN ('reporter', 'staff', 'admin')", name="ck_user_role"),
        CheckConstraint("(is_approved AND role IS NOT NULL AND approved_at IS NOT NULL) OR "
                        "(NOT is_approved AND role IS NULL AND approved_at IS NULL AND approved_by_id IS NULL)",
                        name="ck_user_approval"),
        CheckConstraint("email = lower(email)", name="ck_user_email_normalized"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str | None] = mapped_column(String(20))
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, server_default=sql_text("false"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=sql_text("true"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AssignmentHistory(Base):
    __tablename__ = "assignment_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    previous_assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    changed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClassificationTask(Base):
    __tablename__ = "classification_tasks"
    __table_args__ = (
        CheckConstraint("state IN ('pending', 'running', 'succeeded', 'failed')", name="ck_classification_task_state"),
        Index("uq_active_classification_ticket", "ticket_id", unique=True,
              postgresql_where=sql_text("state IN ('pending', 'running')")),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    content_version: Mapped[int] = mapped_column(Integer)
    run_id: Mapped[str] = mapped_column(String(36))
    state: Mapped[str] = mapped_column(String(20), default=TaskState.PENDING, server_default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class ClassificationReference(Base):
    """Niezależny przykład z ustalonymi etykietami bazowymi, bez reguł operacyjnych."""
    __tablename__ = "classification_references"
    __table_args__ = (
        CheckConstraint("base_priority IN ('low', 'medium', 'high', 'critical')",
                        name="ck_reference_base_priority"),
        CheckConstraint("btrim(category) <> '' AND category <> 'unknown'",
                        name="ck_reference_category"),
        UniqueConstraint("source", "source_key", name="uq_reference_source_key"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50))
    base_priority: Mapped[str] = mapped_column(String(20))
    embedding_vector: Mapped[list[float]] = mapped_column(Vector(384))
    source: Mapped[str] = mapped_column(String(50))
    source_key: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
