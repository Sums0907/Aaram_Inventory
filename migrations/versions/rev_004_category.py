"""Add Category model

Revision ID: rev_004_category
Revises: rev_003_warehouse
Create Date: 2024-01-01 00:00:03.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'rev_004_category'
down_revision: Union[str, None] = 'rev_003_warehouse'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('categories',
        sa.Column('category_code', sa.String(length=50), nullable=False),
        sa.Column('category_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED', name='generic_status', create_type=False), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('category_name')
    )
    op.create_index(op.f('ix_categories_category_code'), 'categories', ['category_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_categories_category_code'), table_name='categories')
    op.drop_table('categories')
