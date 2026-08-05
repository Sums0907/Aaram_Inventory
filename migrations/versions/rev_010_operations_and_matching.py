"""Add Operations and Matching Domains

Revision ID: 010_operations_and_matching
Revises: 009_data_ingestion_pipeline
Create Date: 2026-08-05 07:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '010_operations_and_matching'
down_revision: Union[str, None] = 'rev_009_data_ingestion_pipeline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Operations
    op.create_table('operations_sales_orders',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('external_order_id', sa.String(length=255), nullable=False),
        sa.Column('order_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('platform', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('total_gross', sa.Float(), nullable=False),
        sa.Column('total_tax', sa.Float(), nullable=False),
        sa.Column('total_discount', sa.Float(), nullable=False),
        sa.Column('total_net', sa.Float(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('updated_by', sa.Uuid(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_operations_sales_orders_external_order_id'), 'operations_sales_orders', ['external_order_id'], unique=True)

    op.create_table('operations_sales_order_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('order_id', sa.Uuid(), nullable=False),
        sa.Column('external_sku_code', sa.String(length=255), nullable=False),
        sa.Column('sku_id', sa.Uuid(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('updated_by', sa.Uuid(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['operations_sales_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('operations_tax_invoices',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('invoice_no', sa.String(length=255), nullable=False),
        sa.Column('invoice_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('order_id', sa.Uuid(), nullable=True),
        sa.Column('external_order_id', sa.String(length=255), nullable=False),
        sa.Column('gstin', sa.String(length=15), nullable=True),
        sa.Column('total_base_amount', sa.Float(), nullable=False),
        sa.Column('total_cgst', sa.Float(), nullable=False),
        sa.Column('total_sgst', sa.Float(), nullable=False),
        sa.Column('total_igst', sa.Float(), nullable=False),
        sa.Column('total_tax_amount', sa.Float(), nullable=False),
        sa.Column('total_invoice_amount', sa.Float(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('updated_by', sa.Uuid(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['operations_sales_orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_no')
    )
    
    op.create_table('operations_tax_invoice_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('invoice_id', sa.Uuid(), nullable=False),
        sa.Column('hsn_code', sa.String(length=50), nullable=True),
        sa.Column('sku_id', sa.Uuid(), nullable=True),
        sa.Column('external_sku_code', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('base_amount', sa.Float(), nullable=False),
        sa.Column('tax_rate', sa.Float(), nullable=False),
        sa.Column('cgst_amount', sa.Float(), nullable=False),
        sa.Column('sgst_amount', sa.Float(), nullable=False),
        sa.Column('igst_amount', sa.Float(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('updated_by', sa.Uuid(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['operations_tax_invoices.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('operations_settlements',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('settlement_id', sa.String(length=255), nullable=False),
        sa.Column('settlement_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('platform', sa.String(length=100), nullable=False),
        sa.Column('utr_number', sa.String(length=255), nullable=True),
        sa.Column('gross_amount', sa.Float(), nullable=False),
        sa.Column('fees_amount', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=False),
        sa.Column('net_amount', sa.Float(), nullable=False),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('updated_by', sa.Uuid(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('settlement_id')
    )

    op.create_table('operations_payments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('payment_id', sa.String(length=255), nullable=False),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('platform', sa.String(length=100), nullable=False),
        sa.Column('order_reference', sa.String(length=255), nullable=True),
        sa.Column('external_settlement_id', sa.String(length=255), nullable=True),
        sa.Column('gross_amount', sa.Float(), nullable=False),
        sa.Column('fees_amount', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=False),
        sa.Column('net_amount', sa.Float(), nullable=False),
        sa.Column('matched_order_id', sa.Uuid(), nullable=True),
        sa.Column('settlement_id', sa.Uuid(), nullable=True),
        sa.Column('created_by', sa.Uuid(), nullable=False),
        sa.Column('updated_by', sa.Uuid(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['matched_order_id'], ['operations_sales_orders.id'], ),
        sa.ForeignKeyConstraint(['settlement_id'], ['operations_settlements.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_id')
    )

    # Matching Domain
    op.create_table('matching_jobs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_on', sa.DateTime(timezone=True), nullable=True),
        sa.Column('orders_processed', sa.Integer(), nullable=False),
        sa.Column('payments_processed', sa.Integer(), nullable=False),
        sa.Column('settlements_processed', sa.Integer(), nullable=False),
        sa.Column('invoices_processed', sa.Integer(), nullable=False),
        sa.Column('successful_matches', sa.Integer(), nullable=False),
        sa.Column('failed_matches', sa.Integer(), nullable=False),
        sa.Column('exceptions_generated', sa.Integer(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('matching_relationships',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('match_job_id', sa.Uuid(), nullable=False),
        sa.Column('source_type', sa.String(length=100), nullable=False),
        sa.Column('source_id', sa.Uuid(), nullable=False),
        sa.Column('target_type', sa.String(length=100), nullable=False),
        sa.Column('target_id', sa.Uuid(), nullable=False),
        sa.Column('relationship_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['match_job_id'], ['matching_jobs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_type', 'source_id', 'target_type', 'target_id', 'relationship_type', name='uq_match_relationship')
    )
    op.create_index(op.f('ix_matching_relationships_source_type'), 'matching_relationships', ['source_type'], unique=False)
    op.create_index(op.f('ix_matching_relationships_source_id'), 'matching_relationships', ['source_id'], unique=False)
    op.create_index(op.f('ix_matching_relationships_target_type'), 'matching_relationships', ['target_type'], unique=False)
    op.create_index(op.f('ix_matching_relationships_target_id'), 'matching_relationships', ['target_id'], unique=False)

    op.create_table('matching_exceptions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('match_job_id', sa.Uuid(), nullable=False),
        sa.Column('document_type', sa.String(length=100), nullable=False),
        sa.Column('document_id', sa.Uuid(), nullable=False),
        sa.Column('reason', sa.String(length=1000), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['match_job_id'], ['matching_jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('matching_exceptions')
    op.drop_table('matching_relationships')
    op.drop_table('matching_jobs')
    op.drop_table('operations_payments')
    op.drop_table('operations_settlements')
    op.drop_table('operations_tax_invoice_items')
    op.drop_table('operations_tax_invoices')
    op.drop_table('operations_sales_order_items')
    op.drop_table('operations_sales_orders')
