"""Add partial unique index for active job work rates

Revision ID: 85bbd97c3bd7
Revises: cbdf529beb38
Create Date: 2026-08-13 00:17:31.730845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85bbd97c3bd7'
down_revision: Union[str, None] = 'cbdf529beb38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE UNIQUE INDEX idx_jwa_rates_single_active ON jwa_job_work_rates (job_worker_id, sku_id) WHERE is_active = 1;"
    )


def downgrade() -> None:
    op.execute("DROP INDEX idx_jwa_rates_single_active;")
