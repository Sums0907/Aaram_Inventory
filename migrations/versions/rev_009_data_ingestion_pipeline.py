"""Add data ingestion pipeline models

Revision ID: rev_009_data_ingestion_pipeline
Revises: rev_008_integrations
Create Date: 2024-01-01 00:00:08.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'rev_009_data_ingestion_pipeline'
down_revision: Union[str, None] = 'rev_008_integrations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. import_jobs
    op.create_table('import_jobs',
        sa.Column('integration_id', sa.UUID(), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_import_jobs_integration_id'), 'import_jobs', ['integration_id'], unique=False)

    # 2. import_files
    op.create_table('import_files',
        sa.Column('import_job_id', sa.UUID(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('storage_path', sa.String(length=500), nullable=True),
        sa.Column('md5_hash', sa.String(length=32), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['import_job_id'], ['import_jobs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('import_job_id')
    )
    op.create_index(op.f('ix_import_files_md5_hash'), 'import_files', ['md5_hash'], unique=False)

    # 3. import_records
    op.create_table('import_records',
        sa.Column('import_job_id', sa.UUID(), nullable=False),
        sa.Column('record_type', sa.String(length=50), nullable=False),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('normalized_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['import_job_id'], ['import_jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_import_records_import_job_id'), 'import_records', ['import_job_id'], unique=False)

    # 4. import_errors
    op.create_table('import_errors',
        sa.Column('import_job_id', sa.UUID(), nullable=False),
        sa.Column('import_record_id', sa.UUID(), nullable=True),
        sa.Column('error_code', sa.String(length=100), nullable=False),
        sa.Column('error_message', sa.String(length=1000), nullable=False),
        sa.Column('row_number', sa.Integer(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['import_job_id'], ['import_jobs.id'], ),
        sa.ForeignKeyConstraint(['import_record_id'], ['import_records.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_import_errors_import_job_id'), 'import_errors', ['import_job_id'], unique=False)
    op.create_index(op.f('ix_import_errors_import_record_id'), 'import_errors', ['import_record_id'], unique=False)

    # 5. import_summaries
    op.create_table('import_summaries',
        sa.Column('import_job_id', sa.UUID(), nullable=False),
        sa.Column('total_records', sa.Integer(), nullable=False),
        sa.Column('successful_records', sa.Integer(), nullable=False),
        sa.Column('failed_records', sa.Integer(), nullable=False),
        sa.Column('duplicate_records', sa.Integer(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['import_job_id'], ['import_jobs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('import_job_id')
    )


def downgrade() -> None:
    op.drop_table('import_summaries')
    op.drop_index(op.f('ix_import_errors_import_record_id'), table_name='import_errors')
    op.drop_index(op.f('ix_import_errors_import_job_id'), table_name='import_errors')
    op.drop_table('import_errors')
    op.drop_index(op.f('ix_import_records_import_job_id'), table_name='import_records')
    op.drop_table('import_records')
    op.drop_index(op.f('ix_import_files_md5_hash'), table_name='import_files')
    op.drop_table('import_files')
    op.drop_index(op.f('ix_import_jobs_integration_id'), table_name='import_jobs')
    op.drop_table('import_jobs')
