"""
Job Worker Rate Master.

Defines the labour charge rate for a (job_worker, finished_good_sku) pair.
Rates are versioned by effective_from date — the applicable rate is the one
whose effective_from is ≤ the transaction date.
"""
from uuid import UUID
from datetime import date
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Numeric, ForeignKey, Boolean, Index, text
from src.foundation.database.models import BaseModel


class JobWorkRateModel(BaseModel):
    __tablename__ = "jwa_job_work_rates"

    __table_args__ = (
        Index(
            "uix_active_job_work_rate",
            "job_worker_id",
            "sku_id",
            unique=True,
            sqlite_where=text("is_active = 1"),
            postgresql_where=text("is_active = true")
        ),
    )

    # Who and what
    job_worker_id: Mapped[UUID] = mapped_column(
        ForeignKey("masters_suppliers.id"), nullable=False, index=True
    )
    sku_id: Mapped[UUID] = mapped_column(
        ForeignKey("skus.id"), nullable=False, index=True
    )

    # Rate details
    rate: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    rate_basis: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PER_PIECE"
    )  # PER_PIECE | FIXED

    # Versioning
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Optional notes
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
