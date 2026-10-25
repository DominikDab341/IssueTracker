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
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
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
    # Pole chronione przed zmianą przez formularz; endpoint administratora w E5.9.
    manual_priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    priority_source: Mapped[str] = mapped_column(String(30), default=PrioritySource.LEGACY, server_default="legacy")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    embedding_vector: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)

    @property
    def classification_current(self) -> bool:
        return self.embedding_version is not None and self.embedding_version == self.content_version


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
