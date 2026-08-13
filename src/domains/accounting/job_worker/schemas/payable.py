from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List


class PayableLedgerEntry(BaseModel):
    """One row in the Payable Ledger for a Job Worker."""
    date: date
    particular: str           # "Job Work Charges — <sku_name>" or "Payment"
    reference: str            # GRN number or PAY-xxx
    expense: Optional[float]  # amount if this is a charge row
    payment: Optional[float]  # amount if this is a payment row
    outstanding: float        # running balance
    metadata: Optional[dict] = None  # e.g. quantity, sku_id, rate for GRNs; payment_account, notes for PAY


class JobWorkerPayableSummary(BaseModel):
    job_worker_id: UUID
    job_worker_name: str
    total_expenses: float
    total_paid: float
    outstanding: float


class JobWorkerPayableLedgerResponse(BaseModel):
    job_worker_id: UUID
    job_worker_name: str
    total_expenses: float
    total_paid: float
    outstanding: float
    entries: List[PayableLedgerEntry]


class PayableDashboardResponse(BaseModel):
    total_job_work_expenses: float
    total_paid: float
    total_outstanding: float
    job_workers_with_outstanding: int
    job_workers: List[JobWorkerPayableSummary]
