"""Add gateway_tax to operations_payments

Revision ID: 79e62f22a151
Revises: a7dd4c1026ff
Create Date: 2026-08-05 21:31:49.197313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79e62f22a151'
down_revision: Union[str, None] = 'a7dd4c1026ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('operations_payments', sa.Column('gateway_tax', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0.00'))

def downgrade() -> None:
    op.drop_column('operations_payments', 'gateway_tax')
