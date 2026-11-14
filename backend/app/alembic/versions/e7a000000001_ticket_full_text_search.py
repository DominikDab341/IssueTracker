"""Index the ticket problem description for full-text retrieval."""
from alembic import op
from sqlalchemy import text


revision = "e7a000000001"
down_revision = "e5c000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_tickets_problem_fts", "tickets",
                    [text("to_tsvector('english'::regconfig, text)")], postgresql_using="gin")


def downgrade():
    op.drop_index("ix_tickets_problem_fts", table_name="tickets")
