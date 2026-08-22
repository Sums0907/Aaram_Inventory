"""change_product_description_to_text

Revision ID: a1b2c3d4e5f6
Revises: 6cfa389736fa
Create Date: 2026-08-21 22:36:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6cfa389736fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'products',
        'description',
        existing_type=sa.String(length=1000),
        type_=sa.Text(),
        existing_nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        'products',
        'description',
        existing_type=sa.Text(),
        type_=sa.String(length=1000),
        existing_nullable=True
    )
