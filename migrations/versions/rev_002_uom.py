"""Add Unit of Measure model

Revision ID: rev_002_uom
Revises: rev_001_company
Create Date: 2024-01-01 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'rev_002_uom'
down_revision: Union[str, None] = 'rev_001_company'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('units_of_measure',
        sa.Column('unit_code', sa.String(length=50), nullable=False),
        sa.Column('unit_name', sa.String(length=100), nullable=False),
        sa.Column('short_name', sa.String(length=20), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED', name='generic_status', create_type=False), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('short_name'),
        sa.UniqueConstraint('unit_name')
    )
    op.create_index(op.f('ix_units_of_measure_unit_code'), 'units_of_measure', ['unit_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_units_of_measure_unit_code'), table_name='units_of_measure')
    op.drop_table('units_of_measure')
