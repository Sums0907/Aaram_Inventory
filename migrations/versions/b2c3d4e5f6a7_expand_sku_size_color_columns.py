"""expand_sku_size_color_columns

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-21 22:38:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('skus', 'size',
        existing_type=sa.String(length=50),
        type_=sa.String(length=500),
        existing_nullable=True
    )
    op.alter_column('skus', 'color',
        existing_type=sa.String(length=50),
        type_=sa.String(length=500),
        existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column('skus', 'size',
        existing_type=sa.String(length=500),
        type_=sa.String(length=50),
        existing_nullable=True
    )
    op.alter_column('skus', 'color',
        existing_type=sa.String(length=500),
        type_=sa.String(length=50),
        existing_nullable=True
    )
