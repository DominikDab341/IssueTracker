"""Activate helpdesk categories without guessing a mapping from legacy labels."""
from alembic import op
import sqlalchemy as sa

revision = "e5b000000001"
down_revision = "e2b000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tickets", sa.Column("legacy_category", sa.String(50)))
    op.add_column("tickets", sa.Column("classification_version", sa.String(100)))
    # Preserve the original operational label and all manual/predicted metadata.
    # Reclassification is a separate command, never a model call inside a migration.
    op.execute("UPDATE tickets SET legacy_category=category, category='unknown', embedding_version=NULL "
               "WHERE category NOT IN ('unknown', 'accounts_access', 'hardware', 'network', 'software')")
    op.create_check_constraint("ck_ticket_category", "tickets",
                               "category IN ('unknown', 'accounts_access', 'hardware', 'network', 'software')")
    op.drop_constraint("ck_ticket_manual_category", "tickets", type_="check")
    op.create_check_constraint("ck_ticket_manual_category", "tickets",
                               "manual_category IS NULL OR manual_category IN ('bug', 'performance', 'feature', "
                               "'accounts_access', 'hardware', 'network', 'software')")


def downgrade():
    connection = op.get_bind()
    connection.execute(sa.text("LOCK TABLE tickets IN ACCESS EXCLUSIVE MODE"))
    if connection.scalar(sa.text("SELECT EXISTS(SELECT 1 FROM tickets WHERE legacy_category IS NOT NULL "
                                 "OR classification_version IS NOT NULL OR manual_category IN "
                                 "('accounts_access','hardware','network','software'))")):
        raise RuntimeError("Cofanie migracji utraciłoby historię kategorii lub klasyfikacji.")
    op.drop_constraint("ck_ticket_category", "tickets", type_="check")
    op.drop_constraint("ck_ticket_manual_category", "tickets", type_="check")
    op.create_check_constraint("ck_ticket_manual_category", "tickets",
                               "manual_category IS NULL OR manual_category IN ('bug', 'performance', 'feature')")
    op.drop_column("tickets", "classification_version")
    op.drop_column("tickets", "legacy_category")
