"""Add Product Attribute model

Revision ID: rev_005_product_attribute
Revises: rev_004_category
Create Date: 2024-01-01 00:00:04.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'rev_005_product_attribute'
down_revision: Union[str, None] = 'rev_004_category'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('product_attributes',
        sa.Column('attribute_code', sa.String(length=50), nullable=False),
        sa.Column('attribute_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED', name='generic_status', create_type=False), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('attribute_name')
    )
    op.create_index(op.f('ix_product_attributes_attribute_code'), 'product_attributes', ['attribute_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_product_attributes_attribute_code'), table_name='product_attributes')
    op.drop_table('product_attributes')
