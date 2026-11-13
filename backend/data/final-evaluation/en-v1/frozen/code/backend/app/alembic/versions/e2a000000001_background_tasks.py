"""Persist classification jobs, content versions and priority sources.

Revision ID: e2a000000001
Revises: e1a000000002
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "e2a000000001"
down_revision = "e1a000000002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tickets", sa.Column("work_blocked", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("tickets", sa.Column("content_version", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("tickets", sa.Column("embedding_version", sa.Integer(), nullable=True))
    op.add_column("tickets", sa.Column("current_task_id", sa.String(36), nullable=True))
    for name in ("base_priority", "automatic_priority", "manual_priority"):
        op.add_column("tickets", sa.Column(name, sa.String(20), nullable=True))
    op.add_column("tickets", sa.Column("priority_source", sa.String(30), nullable=False, server_default="legacy"))
    # Zachowujemy stare priorytety, ale nie nazywamy ich przewidywaniem bazowym KNN.
    op.execute("UPDATE tickets SET automatic_priority=priority, embedding_version=CASE WHEN embedding_vector IS NOT NULL THEN 1 ELSE NULL END")
    op.create_table(
        "classification_tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("content_version", sa.Integer(), nullable=False),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column("state", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(30), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("result", JSONB(), nullable=True),
        sa.CheckConstraint("state IN ('pending', 'running', 'succeeded', 'failed')", name="ck_classification_task_state"),
    )
    op.create_index("ix_classification_tasks_ticket_id", "classification_tasks", ["ticket_id"])
    op.create_index("uq_active_classification_ticket", "classification_tasks", ["ticket_id"], unique=True,
                    postgresql_where=sa.text("state IN ('pending', 'running')"))


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT count(*) FROM tickets")):
        raise RuntimeError("Cofanie migracji z danymi utraciłoby zadania i źródła priorytetu. Najpierw przygotuj kontrolowaną migrację danych.")
    op.drop_table("classification_tasks")
    for name in ("priority_source", "manual_priority", "automatic_priority", "base_priority", "current_task_id", "embedding_version", "content_version", "work_blocked"):
        op.drop_column("tickets", name)
