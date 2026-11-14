"""Backfill automatic classification references from resolved tickets."""
from alembic import op


revision = "e8a000000001"
down_revision = "e7a000000001"
branch_labels = None
depends_on = None

_AUDIT_FIELDS = (
    "(source_ticket_id IS NOT NULL AND source_content_version IS NOT NULL "
    "AND source_content_version > 0 AND approved_by_id IS NOT NULL AND approved_at IS NOT NULL)"
)


def upgrade():
    op.drop_constraint("ck_reference_approval", "classification_references", type_="check")
    op.create_check_constraint("ck_reference_approval", "classification_references",
                               "source NOT IN ('approved_ticket', 'resolved_ticket') OR " + _AUDIT_FIELDS)
    op.execute(r"""
        INSERT INTO classification_references (
            text, category, base_priority, embedding_vector, source, source_key,
            source_ticket_id, source_content_version, approved_by_id, approved_at
        )
        SELECT text, category, base_priority, embedding_vector, 'resolved_ticket',
               concat('ticket:', id, '\:v', content_version), id, content_version, resolved_by_id, resolved_at
        FROM tickets
        WHERE status = 'resolved' AND embedding_vector IS NOT NULL AND embedding_version = content_version
          AND category IN ('accounts_access', 'hardware', 'network', 'software')
          AND base_priority IN ('low', 'medium', 'high', 'critical')
          AND resolved_by_id IS NOT NULL AND resolved_at IS NOT NULL
        ON CONFLICT ON CONSTRAINT uq_reference_ticket_version DO NOTHING
    """)


def downgrade():
    op.execute("DELETE FROM classification_references WHERE source = 'resolved_ticket'")
    op.drop_constraint("ck_reference_approval", "classification_references", type_="check")
    op.create_check_constraint("ck_reference_approval", "classification_references",
                               "source <> 'approved_ticket' OR " + _AUDIT_FIELDS)
