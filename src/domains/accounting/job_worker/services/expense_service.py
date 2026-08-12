"""
Job Work Expense Service.

The primary entry point for creating Job Work Expenses.
Normally called by GoodsReceiptService after a JOB_WORK_RECEIPT is posted.
"""
from uuid import UUID
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List
from sqlalchemy import select
from src.foundation.database.models import SequenceModel
from src.domains.accounting.job_worker.repositories.expenses import JobWorkExpenseRepository
from src.domains.accounting.job_worker.repositories.rates import JobWorkRateRepository
from src.domains.accounting.job_worker.models.job_work_expense import JobWorkExpenseModel
from src.domains.accounting.job_worker.schemas.job_work_expense import JobWorkExpenseCreate
from src.foundation.exceptions.base import ValidationException


async def _next_seq(session, prefix: str) -> str:
    """Transaction-safe sequence using shared SequenceModel table."""
    stmt = select(SequenceModel).where(
        SequenceModel.sequence_name == prefix
    ).with_for_update()
    res = await session.execute(stmt)
    seq = res.scalars().first()
    if not seq:
        seq = SequenceModel(sequence_name=prefix, last_value=1)
        session.add(seq)
        return f"{prefix}-001"
    seq.last_value += 1
    return f"{prefix}-{seq.last_value:03d}"


class ExpenseService:
    def __init__(
        self,
        expense_repository: JobWorkExpenseRepository,
        rate_repository: JobWorkRateRepository,
    ):
        self.expense_repo = expense_repository
        self.rate_repo = rate_repository

    @property
    def _session(self):
        return self.expense_repo.session

    async def create_from_receipt(
        self,
        job_worker_id: UUID,
        sku_id: UUID,
        quantity: float,
        receipt_id: UUID,
        receipt_number: str,
        receipt_date: date,
        created_by: UUID,
        rate_override: Optional[float] = None,
    ) -> Optional[JobWorkExpenseModel]:
        """
        Called by GoodsReceiptService after a JOB_WORK_RECEIPT is posted.

        Returns:
            The created JobWorkExpenseModel, or None if no rate is configured
            and rate_override is also not provided.

        Raises:
            ValidationException if a duplicate expense for this receipt already exists.
        """
        # Guard: no duplicate expense for same receipt
        if await self.expense_repo.exists_for_receipt(receipt_id):
            raise ValidationException(
                f"An expense already exists for receipt {receipt_number}. Duplicate prevented."
            )

        # Determine rate
        if rate_override is not None:
            rate = Decimal(str(rate_override))
            rate_basis = "PER_PIECE"
        else:
            rate_model = await self.rate_repo.get_applicable_rate(
                job_worker_id, sku_id, receipt_date
            )
            if rate_model is None:
                # No rate configured — return None, the caller handles the warning
                return None
            rate = Decimal(str(rate_model.rate))
            rate_basis = rate_model.rate_basis

        qty = Decimal(str(quantity))
        amount = (qty * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        today = date.today()
        prefix = f"JWE-{today.strftime('%d%m%y')}"
        reference = await _next_seq(self._session, prefix)

        expense = JobWorkExpenseModel(
            reference=reference,
            job_worker_id=job_worker_id,
            finished_product_id=sku_id,
            quantity=qty,
            rate=rate,
            rate_basis=rate_basis,
            amount=amount,
            source_receipt_id=receipt_id,
            source_receipt_number=receipt_number,
            expense_date=receipt_date,
            status="POSTED",
            created_by=created_by,
            updated_by=created_by,
        )
        await self.expense_repo.create(expense)
        return expense

    async def create_manual(
        self, schema: JobWorkExpenseCreate, created_by: UUID
    ) -> JobWorkExpenseModel:
        """Manual expense creation (admin / correction)."""
        qty = Decimal(str(schema.quantity))
        rate = Decimal(str(schema.rate))
        amount = (qty * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        today = date.today()
        prefix = f"JWE-{today.strftime('%d%m%y')}"
        reference = await _next_seq(self._session, prefix)

        expense = JobWorkExpenseModel(
            reference=reference,
            job_worker_id=schema.job_worker_id,
            finished_product_id=schema.finished_product_id,
            quantity=qty,
            rate=rate,
            rate_basis=schema.rate_basis,
            amount=amount,
            source_receipt_id=schema.source_receipt_id,
            source_receipt_number=schema.source_receipt_number,
            expense_date=schema.expense_date,
            status="POSTED",
            created_by=created_by,
            updated_by=created_by,
        )
        await self.expense_repo.create(expense)
        return expense

    async def get_all_for_worker(self, job_worker_id: UUID) -> List[JobWorkExpenseModel]:
        return await self.expense_repo.get_all_for_worker(job_worker_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[JobWorkExpenseModel]:
        return await self.expense_repo.get_all(skip, limit)
