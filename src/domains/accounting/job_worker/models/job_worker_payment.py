"""
Job Worker Payment.

An independent financial event representing money paid to a Job Worker.
Does NOT create or modify any expense. Outstanding is derived as:
    SUM(expenses.amount) - SUM(payments.amount)
"""
from uuid import UUID
from datetime import date
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Numeric, ForeignKey
from src.foundation.database.models import BaseModel


class JobWorkerPaymentModel(BaseModel):
    __tablename__ = "jwa_job_worker_payments"

    reference: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )  # e.g. PAY-120826-001

    job_worker_id: Mapped[UUID] = mapped_column(
        ForeignKey("masters_suppliers.id"), nullable=False, index=True
    )

    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # Where payment came from (e.g. "Axis Bank", "Cash", "UPI")
    payment_account: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # UTR / Cheque number / Transaction ID
    payment_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="POSTED"
    )  # POSTED | CANCELLED
