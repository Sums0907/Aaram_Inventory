"""add_inventory_truth_engine_rc1

Revision ID: e06b777bd136
Revises: 79e62f22a151
Create Date: 2026-08-06 01:37:29.810689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e06b777bd136'
down_revision: Union[str, None] = '79e62f22a151'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'inventory_balances',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('warehouse_id', sa.Uuid(), nullable=False),
        sa.Column('sku_id', sa.Uuid(), nullable=False),
        sa.Column('quantity_on_hand', sa.Integer(), nullable=False),
        sa.Column('confidence_score', sa.Integer(), nullable=False),
        sa.Column('confidence_reasons', sa.JSON(), nullable=False),
        sa.Column('last_movement_date', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('warehouse_id', 'sku_id', name='uq_inventory_balance_warehouse_sku')
    )
    op.create_index(op.f('ix_inventory_balances_sku_id'), 'inventory_balances', ['sku_id'], unique=False)
    op.create_index(op.f('ix_inventory_balances_warehouse_id'), 'inventory_balances', ['warehouse_id'], unique=False)

    op.create_table(
        'inventory_exceptions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=True),
        sa.Column('updated_by', sa.Uuid(), nullable=True),
        sa.Column('exception_number', sa.String(length=255), nullable=False),
        sa.Column('warehouse_id', sa.Uuid(), nullable=False),
        sa.Column('sku_id', sa.Uuid(), nullable=False),
        sa.Column('exception_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source_system', sa.String(length=100), nullable=False),
        sa.Column('expected_quantity', sa.Integer(), nullable=False),
        sa.Column('actual_quantity', sa.Integer(), nullable=False),
        sa.Column('difference', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('resolution_notes', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['sku_id'], ['skus.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_exceptions_exception_number'), 'inventory_exceptions', ['exception_number'], unique=True)
    op.create_index(op.f('ix_inventory_exceptions_sku_id'), 'inventory_exceptions', ['sku_id'], unique=False)
    op.create_index(op.f('ix_inventory_exceptions_warehouse_id'), 'inventory_exceptions', ['warehouse_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_inventory_exceptions_warehouse_id'), table_name='inventory_exceptions')
    op.drop_index(op.f('ix_inventory_exceptions_sku_id'), table_name='inventory_exceptions')
    op.drop_index(op.f('ix_inventory_exceptions_exception_number'), table_name='inventory_exceptions')
    op.drop_table('inventory_exceptions')
    op.drop_index(op.f('ix_inventory_balances_warehouse_id'), table_name='inventory_balances')
    op.drop_index(op.f('ix_inventory_balances_sku_id'), table_name='inventory_balances')
    op.drop_table('inventory_balances')
