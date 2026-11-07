"""Reviewed ticket references, explicit decision review and persistent escalation."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "e5c000000001"
down_revision = "e5b000000001"
branch_labels = None
depends_on = None

TICKET_COLUMNS = {
    "predicted_base_priority": sa.String(20), "category_score": sa.Float(), "priority_score": sa.Float(),
    "category_review_reason": sa.String(100), "priority_review_reason": sa.String(100),
    "review_version": sa.Integer(), "escalation_min_priority": sa.String(20),
    "escalated_at": sa.DateTime(timezone=True), "escalation_reason": sa.Text(), "escalation_evidence": JSONB(),
}


def upgrade():
    for name, kind in TICKET_COLUMNS.items():
        op.add_column("tickets", sa.Column(name, kind))
    op.create_check_constraint("ck_ticket_escalation_min", "tickets", "escalation_min_priority IS NULL OR escalation_min_priority = 'high'")
    op.create_check_constraint("ck_ticket_escalation_metadata", "tickets",
        "(escalation_min_priority IS NULL AND escalated_at IS NULL AND escalation_reason IS NULL) OR "
        "(escalation_min_priority IS NOT NULL AND escalated_at IS NOT NULL AND escalation_reason IS NOT NULL)")
    op.add_column("classification_references", sa.Column("source_ticket_id", sa.Integer(),
                  sa.ForeignKey("tickets.id", name="fk_reference_source_ticket")))
    op.add_column("classification_references", sa.Column("source_content_version", sa.Integer()))
    op.add_column("classification_references", sa.Column("approved_by_id", sa.Integer(),
                  sa.ForeignKey("users.id", name="fk_reference_approved_by")))
    op.add_column("classification_references", sa.Column("approved_at", sa.DateTime(timezone=True)))
    op.create_unique_constraint("uq_reference_ticket_version", "classification_references", ["source_ticket_id", "source_content_version"])
    op.create_check_constraint("ck_reference_approval", "classification_references",
        "source <> 'approved_ticket' OR (source_ticket_id IS NOT NULL AND source_content_version IS NOT NULL AND source_content_version > 0 "
        "AND approved_by_id IS NOT NULL AND approved_at IS NOT NULL)")


def downgrade():
    db = op.get_bind()
    db.execute(sa.text("LOCK TABLE tickets, classification_references IN ACCESS EXCLUSIVE MODE"))
    fields = " OR ".join(f"{name} IS NOT NULL" for name in TICKET_COLUMNS)
    if db.scalar(sa.text(f"SELECT EXISTS(SELECT 1 FROM tickets WHERE {fields}) "
                         "OR EXISTS(SELECT 1 FROM classification_references WHERE source_ticket_id IS NOT NULL "
                         "OR source_content_version IS NOT NULL OR approved_by_id IS NOT NULL OR approved_at IS NOT NULL)")):
        raise RuntimeError("Cofanie migracji utraciłoby decyzje weryfikacji, referencje lub eskalacje.")
    op.drop_constraint("ck_reference_approval", "classification_references", type_="check")
    op.drop_constraint("uq_reference_ticket_version", "classification_references", type_="unique")
    op.drop_constraint("fk_reference_source_ticket", "classification_references", type_="foreignkey")
    op.drop_constraint("fk_reference_approved_by", "classification_references", type_="foreignkey")
    for name in ("approved_at", "approved_by_id", "source_content_version", "source_ticket_id"):
        op.drop_column("classification_references", name)
    op.drop_constraint("ck_ticket_escalation_min", "tickets", type_="check")
    op.drop_constraint("ck_ticket_escalation_metadata", "tickets", type_="check")
    for name in reversed(TICKET_COLUMNS):
        op.drop_column("tickets", name)
