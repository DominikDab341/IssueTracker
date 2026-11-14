"""Store users' given and family names."""
import sqlalchemy as sa
from alembic import op


revision = "e9a000000001"
down_revision = "e8a000000001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("first_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(100), nullable=True))
    op.create_check_constraint("ck_user_name_pair", "users", "(first_name IS NULL) = (last_name IS NULL)")


def downgrade():
    op.drop_constraint("ck_user_name_pair", "users", type_="check")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
