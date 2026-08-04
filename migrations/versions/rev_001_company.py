"""Add Company model

Revision ID: rev_001_company
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'rev_001_company'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create ENUM types
    op.execute("CREATE TYPE generic_status AS ENUM ('ACTIVE', 'INACTIVE', 'ARCHIVED')")

    op.create_table('companies',
        sa.Column('company_code', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('gstin', sa.String(length=15), nullable=False),
        sa.Column('pan', sa.String(length=10), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('mobile', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('address_line_1', sa.String(length=255), nullable=False),
        sa.Column('address_line_2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('pin_code', sa.String(length=20), nullable=False),
        sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED', name='generic_status', create_type=False), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_name'),
        sa.UniqueConstraint('gstin'),
        sa.UniqueConstraint('pan')
    )
    op.create_index(op.f('ix_companies_company_code'), 'companies', ['company_code'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_companies_company_code'), table_name='companies')
    op.drop_table('companies')
    op.execute("DROP TYPE generic_status")
