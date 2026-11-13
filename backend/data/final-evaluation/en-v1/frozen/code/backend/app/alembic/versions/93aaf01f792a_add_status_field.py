"""add_status_field

Revision ID: 93aaf01f792a
Revises: 01dc9b5e8ac2
Create Date: 2026-04-06 23:53:30.602034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93aaf01f792a'
down_revision: Union[str, Sequence[str], None] = '01dc9b5e8ac2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tickets', sa.Column(
        'status', sa.String(20), nullable=False, server_default='open'
    ))
    op.create_check_constraint(
        'ck_ticket_status', 'tickets',
        "status IN ('open', 'resolved', 'closed')"
    )


def downgrade() -> None:
    op.drop_constraint('ck_ticket_status', 'tickets')
    op.drop_column('tickets', 'status')

