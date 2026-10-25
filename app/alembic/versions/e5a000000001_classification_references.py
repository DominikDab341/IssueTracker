"""Separate KNN references from operational tickets and their final priorities.

Revision ID: e5a000000001
Revises: e2a000000001
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = "e5a000000001"
down_revision = "e2a000000001"
branch_labels = None
depends_on = None


def upgrade():
    # Nie kopiujemy priorytetów ani przewidywań istniejących spraw do referencji.
    op.create_table(
        "classification_references",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("base_priority", sa.String(20), nullable=False),
        sa.Column("embedding_vector", Vector(384), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_key", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("base_priority IN ('low', 'medium', 'high', 'critical')",
                           name="ck_reference_base_priority"),
        sa.CheckConstraint("btrim(category) <> '' AND category <> 'unknown'",
                           name="ck_reference_category"),
        sa.UniqueConstraint("source", "source_key", name="uq_reference_source_key"),
    )


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT count(*) FROM classification_references")):
        raise RuntimeError("Cofanie migracji utraciłoby przykłady referencyjne. Najpierw przygotuj kontrolowaną migrację danych.")
    op.drop_table("classification_references")
