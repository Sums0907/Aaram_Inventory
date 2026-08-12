"""
Payable Allocation (FIFO).

Links payments to specific expenses for audit trail.
Created automatically when a payment is recorded —
oldest outstanding expense is settled first (FIFO).
"""
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, ForeignKey
from src.foundation.database.models import BaseModel


class PayableAllocationModel(BaseModel):
    __tablename__ = "jwa_payable_allocations"

    expense_id: Mapped[UUID] = mapped_column(
        ForeignKey("jwa_job_work_expenses.id"), nullable=False, index=True
    )
    payment_id: Mapped[UUID] = mapped_column(
        ForeignKey("jwa_job_worker_payments.id"), nullable=False, index=True
    )
    allocated_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
