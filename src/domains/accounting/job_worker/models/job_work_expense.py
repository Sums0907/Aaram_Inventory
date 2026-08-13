"""
Job Work Expense.

Automatically created when a JOB_WORK_RECEIPT is posted by the Inventory module.
The rate is a SNAPSHOT taken at the time of creation — changing the Rate Master
later does NOT change historical expenses.
"""
from uuid import UUID
from datetime import date
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Numeric, ForeignKey
from src.foundation.database.models import BaseModel


class JobWorkExpenseModel(BaseModel):
    __tablename__ = "jwa_job_work_expenses"

    # Reference
    reference: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )  # e.g. JWE-120826-001

    # Who
    job_worker_id: Mapped[UUID] = mapped_column(
        ForeignKey("masters_suppliers.id"), nullable=False, index=True
    )

    # What was produced (finished good SKU)
    finished_product_id: Mapped[UUID] = mapped_column(
        ForeignKey("skus.id"), nullable=False, index=True
    )

    # How many
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)

    # Rate snapshot (immutable after creation)
    rate: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    rate_basis: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PER_PIECE"
    )
    rate_version_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("jwa_job_work_rates.id"), nullable=True
    )

    # Financial result
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Source reference back to Inventory
    source_receipt_id: Mapped[Optional[UUID]] = mapped_column(
        nullable=True, index=True
    )  # UUID of the GoodsReceipt (Inventory side — no FK to avoid cross-domain coupling)
    source_receipt_number: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )  # GRN number string for display e.g. "GRN-001"

    # Dates & status
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="POSTED"
    )  # POSTED | CANCELLED

    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
