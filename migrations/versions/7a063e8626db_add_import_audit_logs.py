"""add_import_audit_logs

Revision ID: 7a063e8626db
Revises: f4eb68aad924
Create Date: 2026-08-18 18:22:07.275931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a063e8626db'
down_revision: Union[str, None] = 'f4eb68aad924'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('import_audit_logs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('batch_id', sa.String(length=50), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('entity_type', sa.String(length=100), nullable=False),
    sa.Column('environment', sa.String(length=50), nullable=False),
    sa.Column('executed_by_user_id', sa.Uuid(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('rollback_status', sa.String(length=50), nullable=True),
    sa.Column('records_processed', sa.Integer(), nullable=False),
    sa.Column('success_count', sa.Integer(), nullable=False),
    sa.Column('failure_count', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_import_audit_logs_batch_id'), 'import_audit_logs', ['batch_id'], unique=False)
    op.create_index(op.f('ix_import_audit_logs_entity_type'), 'import_audit_logs', ['entity_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_import_audit_logs_entity_type'), table_name='import_audit_logs')
    op.drop_index(op.f('ix_import_audit_logs_batch_id'), table_name='import_audit_logs')
    op.drop_table('import_audit_logs')
