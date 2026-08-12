"""
Payable Service.

Derives outstanding balances and builds the Payable Ledger.
All balances are derived from immutable expense and payment records.
"""
from uuid import UUID
from decimal import Decimal
from typing import List
from src.domains.accounting.job_worker.repositories.expenses import JobWorkExpenseRepository
from src.domains.accounting.job_worker.repositories.payments import JobWorkerPaymentRepository
from src.domains.accounting.job_worker.repositories.payable import PayableRepository
from src.domains.accounting.job_worker.schemas.payable import (
    PayableLedgerEntry,
    JobWorkerPayableLedgerResponse,
    PayableDashboardResponse,
    JobWorkerPayableSummary,
)


class PayableService:
    def __init__(
        self,
        expense_repository: JobWorkExpenseRepository,
        payment_repository: JobWorkerPaymentRepository,
        payable_repository: PayableRepository,
    ):
        self.expense_repo = expense_repository
        self.payment_repo = payment_repository
        self.payable_repo = payable_repository

    async def get_payable_ledger(
        self, job_worker_id: UUID, job_worker_name: str
    ) -> JobWorkerPayableLedgerResponse:
        expenses = await self.expense_repo.get_all_for_worker(job_worker_id)
        payments = await self.payment_repo.get_all_for_worker(job_worker_id)

        # Build chronological entries
        entries: List[dict] = []
        for e in expenses:
            created = e.created_on.replace(tzinfo=None) if e.created_on else e.expense_date
            entries.append({
                "date": e.expense_date,
                "particular": f"Job Work Charges",
                "reference": e.source_receipt_number or e.reference,
                "expense": float(e.amount),
                "payment": None,
                "sort_key": (e.expense_date, created),
            })
        for p in payments:
            created = p.created_on.replace(tzinfo=None) if p.created_on else p.payment_date
            entries.append({
                "date": p.payment_date,
                "particular": "Payment",
                "reference": p.reference,
                "expense": None,
                "payment": float(p.amount),
                "sort_key": (p.payment_date, created),
            })

        entries.sort(key=lambda x: x["sort_key"])

        running = Decimal("0.00")
        ledger_entries = []
        for e in entries:
            if e["expense"] is not None:
                running += Decimal(str(e["expense"]))
            else:
                running -= Decimal(str(e["payment"]))
            ledger_entries.append(
                PayableLedgerEntry(
                    date=e["date"],
                    particular=e["particular"],
                    reference=e["reference"],
                    expense=e["expense"],
                    payment=e["payment"],
                    outstanding=float(running),
                )
            )

        total_exp = sum(Decimal(str(e.amount)) for e in expenses)
        total_paid = sum(Decimal(str(p.amount)) for p in payments)

        return JobWorkerPayableLedgerResponse(
            job_worker_id=job_worker_id,
            job_worker_name=job_worker_name,
            total_expenses=float(total_exp),
            total_paid=float(total_paid),
            outstanding=float(total_exp - total_paid),
            entries=ledger_entries,
        )

    async def get_dashboard(self, job_workers: list) -> PayableDashboardResponse:
        """
        job_workers: list of (id, name) tuples for active job workers.
        """
        total_exp, total_paid = await self.payable_repo.get_global_totals()
        outstanding = total_exp - total_paid

        summaries = []
        workers_with_outstanding = 0
        for jw_id, jw_name in job_workers:
            exp, paid = await self.payable_repo.get_totals_for_worker(jw_id)
            out = exp - paid
            if out > 0:
                workers_with_outstanding += 1
            summaries.append(
                JobWorkerPayableSummary(
                    job_worker_id=jw_id,
                    job_worker_name=jw_name,
                    total_expenses=float(exp),
                    total_paid=float(paid),
                    outstanding=float(out),
                )
            )

        # Sort by outstanding desc
        summaries.sort(key=lambda x: x.outstanding, reverse=True)

        return PayableDashboardResponse(
            total_job_work_expenses=float(total_exp),
            total_paid=float(total_paid),
            total_outstanding=float(outstanding),
            job_workers_with_outstanding=workers_with_outstanding,
            job_workers=summaries,
        )
