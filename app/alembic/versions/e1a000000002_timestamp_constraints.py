"""Align timestamp nullability with ORM and API.

Revision ID: e1a000000002
Revises: e1a000000001
"""
from alembic import op
import sqlalchemy as sa

revision = "e1a000000002"
down_revision = "e1a000000001"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    connection.execute(sa.text("LOCK TABLE tickets IN ACCESS EXCLUSIVE MODE"))
    if connection.scalar(sa.text("SELECT count(*) FROM tickets WHERE created_at IS NULL OR updated_at IS NULL")):
        raise RuntimeError("Istnieją zgłoszenia bez dat. Uzgodnij uzupełnienie dat przed migracją; nie przypisujemy dat arbitralnie.")
    op.alter_column("tickets", "created_at", nullable=False)
    op.alter_column("tickets", "updated_at", nullable=False)


def downgrade():
    op.alter_column("tickets", "created_at", nullable=True)
    op.alter_column("tickets", "updated_at", nullable=True)
