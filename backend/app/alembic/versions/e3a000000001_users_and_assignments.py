"""Users, decision authors and assignment history; preserve unowned legacy rows."""
from alembic import op
import sqlalchemy as sa

revision = "e3a000000001"
down_revision = "e5a000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(20)),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("approved_by_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IS NULL OR role IN ('reporter', 'staff', 'admin')", name="ck_user_role"),
        sa.CheckConstraint("(is_approved AND role IS NOT NULL AND approved_at IS NOT NULL) OR "
                           "(NOT is_approved AND role IS NULL AND approved_at IS NULL AND approved_by_id IS NULL)",
                           name="ck_user_approval"),
        sa.CheckConstraint("email = lower(email)", name="ck_user_email_normalized"),
    )
    for field in ("author_id", "assignee_id", "status_changed_by_id", "resolved_by_id", "rejected_by_id", "manual_priority_by_id"):
        op.add_column("tickets", sa.Column(field, sa.Integer(), sa.ForeignKey("users.id", name=f"fk_tickets_{field}")))
    for field in ("status_changed_at", "manual_priority_at"):
        op.add_column("tickets", sa.Column(field, sa.DateTime(timezone=True)))
    # Wyjątek jest jawny i dotyczy tylko danych istniejących przed kontami.
    op.add_column("tickets", sa.Column("legacy_unowned", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.alter_column("tickets", "legacy_unowned", server_default=sa.false())
    op.create_check_constraint("ck_ticket_author", "tickets", "author_id IS NOT NULL OR legacy_unowned")
    op.create_index("ix_tickets_author_id", "tickets", ["author_id"])
    op.create_index("ix_tickets_assignee_id", "tickets", ["assignee_id"])
    op.create_table(
        "assignment_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_id", sa.Integer(), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("previous_assignee_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("assignee_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("changed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_assignment_history_ticket_id", "assignment_history", ["ticket_id"])


def downgrade():
    db = op.get_bind()
    if db.scalar(sa.text("SELECT EXISTS(SELECT 1 FROM users) OR EXISTS(SELECT 1 FROM assignment_history)")):
        raise RuntimeError("Cofanie migracji utraciłoby konta lub decyzje. Przygotuj kontrolowaną migrację danych.")
    op.drop_table("assignment_history")
    op.drop_index("ix_tickets_author_id", table_name="tickets")
    op.drop_index("ix_tickets_assignee_id", table_name="tickets")
    op.drop_constraint("ck_ticket_author", "tickets", type_="check")
    for field in ("legacy_unowned", "manual_priority_at", "status_changed_at", "manual_priority_by_id",
                  "rejected_by_id", "resolved_by_id", "status_changed_by_id", "assignee_id", "author_id"):
        op.drop_column("tickets", field)
    op.drop_table("users")
