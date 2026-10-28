"""Six workflow statuses; require explicit decisions for legacy data.

Revision ID: e1a000000001
Revises: 93aaf01f792a
"""
import json

from alembic import context, op
import sqlalchemy as sa

revision = "e1a000000001"
down_revision = "93aaf01f792a"
branch_labels = None
depends_on = None

NEW_STATUSES = {"reported", "accepted", "in_progress", "resolved", "rejected", "cancelled"}


def upgrade():
    connection = op.get_bind()
    # Nie zgadujemy znaczenia open/closed. Odczyt i aktualizacja są w jednej
    # transakcji; blokada uniemożliwia dopisanie starego statusu w trakcie migracji.
    connection.execute(sa.text("LOCK TABLE tickets IN ACCESS EXCLUSIVE MODE"))
    counts = dict(connection.execute(sa.text("SELECT status, count(*) FROM tickets GROUP BY status")).all())
    mapping = json.loads(context.get_x_argument(as_dictionary=True).get("legacy_status_map", "{}"))
    if not isinstance(mapping, dict) or any(k not in {"open", "resolved", "closed"} or v not in NEW_STATUSES for k, v in mapping.items()):
        raise RuntimeError("legacy_status_map musi mapować stare statusy na sześć dozwolonych statusów.")
    # Również stare resolved wymaga jawnej decyzji o zachowaniu znaczenia.
    if counts and set(counts) - set(mapping):
        raise RuntimeError(
            f"Istniejące rekordy: {counts}. Uzgodnij zachowanie danych i podaj "
            "-x legacy_status_map z jawnym mapowaniem każdego występującego statusu. "
            "Migracja nie zmieniła danych."
        )
    op.drop_constraint("ck_ticket_status", "tickets", type_="check")
    if mapping:
        tickets = sa.table("tickets", sa.column("status", sa.String()))
        connection.execute(tickets.update().values(status=sa.case(mapping, value=tickets.c.status, else_=tickets.c.status)))
    op.alter_column("tickets", "status", server_default="reported")
    op.create_check_constraint("ck_ticket_status", "tickets", "status IN ('reported', 'accepted', 'in_progress', 'resolved', 'rejected', 'cancelled')")
    op.add_column("tickets", sa.Column("resolution_note", sa.Text(), nullable=True))
    op.add_column("tickets", sa.Column("rejection_reason", sa.Text(), nullable=True))
    op.add_column("tickets", sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("tickets", sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    connection = op.get_bind()
    connection.execute(sa.text("LOCK TABLE tickets IN ACCESS EXCLUSIVE MODE"))
    if connection.scalar(sa.text("SELECT count(*) FROM tickets")):
        raise RuntimeError("Cofanie migracji z danymi utraciłoby statusy i notatki. Najpierw przygotuj kontrolowaną migrację danych.")
    for column in ("rejected_at", "resolved_at", "rejection_reason", "resolution_note"):
        op.drop_column("tickets", column)
    op.drop_constraint("ck_ticket_status", "tickets", type_="check")
    op.alter_column("tickets", "status", server_default="open")
    op.create_check_constraint("ck_ticket_status", "tickets", "status IN ('open', 'resolved', 'closed')")
