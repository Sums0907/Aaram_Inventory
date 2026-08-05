"""Add integrations domain

Revision ID: rev_008_integrations
Revises: rev_007_sku
Create Date: 2024-01-01 00:00:07.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'rev_008_integrations'
down_revision: Union[str, None] = 'rev_007_sku'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('integrations',
        sa.Column('integration_code', sa.String(length=50), nullable=False),
        sa.Column('integration_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('integration_type', sa.String(length=50), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED', name='generic_status', create_type=False), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_integrations_integration_code'), 'integrations', ['integration_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_integrations_integration_code'), table_name='integrations')
    op.drop_table('integrations')
