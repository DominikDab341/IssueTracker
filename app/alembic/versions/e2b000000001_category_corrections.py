"""Separate operational category corrections from KNN predictions (E2.5)."""
from alembic import op
import sqlalchemy as sa

revision = "e2b000000001"
down_revision = "e3a000000001"
branch_labels = None
depends_on = None


def upgrade():
    # Nie zgadujemy, czy dawna kategoria operacyjna była wynikiem KNN.
    for field in ("predicted_category", "manual_category"):
        op.add_column("tickets", sa.Column(field, sa.String(50)))
    for field in ("predicted_category_version", "manual_category_version"):
        op.add_column("tickets", sa.Column(field, sa.Integer()))
    op.add_column("tickets", sa.Column("manual_category_by_id", sa.Integer(),
                                       sa.ForeignKey("users.id", name="fk_tickets_manual_category_by_id")))
    op.add_column("tickets", sa.Column("manual_category_at", sa.DateTime(timezone=True)))
    op.create_check_constraint("ck_ticket_manual_category", "tickets",
                               "manual_category IS NULL OR manual_category IN ('bug', 'performance', 'feature')")
    op.create_check_constraint("ck_ticket_manual_category_metadata", "tickets",
                               "(manual_category IS NULL AND manual_category_version IS NULL AND "
                               "manual_category_by_id IS NULL AND manual_category_at IS NULL) OR "
                               "(manual_category IS NOT NULL AND manual_category_version IS NOT NULL AND "
                               "manual_category_by_id IS NOT NULL AND manual_category_at IS NOT NULL AND "
                               "manual_category_version > 0 AND manual_category_version <= content_version)")


def downgrade():
    connection = op.get_bind()
    connection.execute(sa.text("LOCK TABLE tickets IN ACCESS EXCLUSIVE MODE"))
    if connection.scalar(sa.text("SELECT EXISTS(SELECT 1 FROM tickets WHERE predicted_category IS NOT NULL "
                                 "OR predicted_category_version IS NOT NULL OR manual_category IS NOT NULL "
                                 "OR manual_category_version IS NOT NULL OR manual_category_by_id IS NOT NULL "
                                 "OR manual_category_at IS NOT NULL)")):
        raise RuntimeError("Cofanie migracji utraciłoby przewidywania lub korekty kategorii. Przygotuj kontrolowaną migrację danych.")
    op.drop_constraint("ck_ticket_manual_category_metadata", "tickets", type_="check")
    op.drop_constraint("ck_ticket_manual_category", "tickets", type_="check")
    for field in ("manual_category_at", "manual_category_by_id", "manual_category_version", "manual_category",
                  "predicted_category_version", "predicted_category"):
        op.drop_column("tickets", field)
