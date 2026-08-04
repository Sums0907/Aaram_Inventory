"""Add SKU model

Revision ID: rev_007_sku
Revises: rev_006_inventory_item
Create Date: 2024-01-01 00:00:06.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'rev_007_sku'
down_revision: Union[str, None] = 'rev_006_inventory_item'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('skus',
        sa.Column('sku_code', sa.String(length=50), nullable=False),
        sa.Column('sku_name', sa.String(length=100), nullable=False),
        sa.Column('inventory_item_id', sa.UUID(), nullable=False),
        sa.Column('attribute_values', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('barcode', sa.String(length=100), nullable=True),
        sa.Column('hsn_code', sa.String(length=20), nullable=True),
        sa.Column('gst_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED', name='generic_status', create_type=False), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('barcode')
    )
    op.create_index(op.f('ix_skus_sku_code'), 'skus', ['sku_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_skus_sku_code'), table_name='skus')
    op.drop_table('skus')
