"""Add Inventory Item model

Revision ID: rev_006_inventory_item
Revises: rev_005_product_attribute
Create Date: 2024-01-01 00:00:05.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'rev_006_inventory_item'
down_revision: Union[str, None] = 'rev_005_product_attribute'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('inventory_items',
        sa.Column('item_code', sa.String(length=50), nullable=False),
        sa.Column('item_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('category_id', sa.UUID(), nullable=False),
        sa.Column('unit_of_measure_id', sa.UUID(), nullable=False),
        sa.Column('hsn_code', sa.String(length=20), nullable=True),
        sa.Column('gst_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED', name='generic_status', create_type=False), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['unit_of_measure_id'], ['units_of_measure.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_items_item_code'), 'inventory_items', ['item_code'], unique=True)
    
    op.create_table('inventory_item_attributes',
        sa.Column('inventory_item_id', sa.UUID(), nullable=False),
        sa.Column('product_attribute_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_items.id'], ),
        sa.ForeignKeyConstraint(['product_attribute_id'], ['product_attributes.id'], ),
        sa.PrimaryKeyConstraint('inventory_item_id', 'product_attribute_id')
    )


def downgrade() -> None:
    op.drop_table('inventory_item_attributes')
    op.drop_index(op.f('ix_inventory_items_item_code'), table_name='inventory_items')
    op.drop_table('inventory_items')
