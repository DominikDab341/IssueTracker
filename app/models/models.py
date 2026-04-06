from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database.database import Base
from pgvector.sqlalchemy import Vector


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'resolved', 'closed')",
            name="ck_ticket_status"
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20),nullable=False, default="open")
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    embedding_vector: Mapped[list[float]] = mapped_column(Vector(384), nullable=True)