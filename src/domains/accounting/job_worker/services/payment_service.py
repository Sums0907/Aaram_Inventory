"""
Job Worker Payment Service.

Records payments and applies FIFO allocation against outstanding expenses.
"""
from uuid import UUID
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List
from sqlalchemy import select
from src.foundation.database.models import SequenceModel
from src.domains.accounting.job_worker.repositories.payments import JobWorkerPaymentRepository
from src.domains.accounting.job_worker.repositories.expenses import JobWorkExpenseRepository
from src.domains.accounting.job_worker.repositories.payable import PayableRepository
from src.domains.accounting.job_worker.models.job_worker_payment import JobWorkerPaymentModel
from src.domains.accounting.job_worker.models.payable_allocation import PayableAllocationModel
from src.domains.accounting.job_worker.schemas.job_worker_payment import JobWorkerPaymentCreate
from src.foundation.exceptions.base import ValidationException


async def _next_seq(session, prefix: str) -> str:
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


class PaymentService:
    def __init__(
        self,
        payment_repository: JobWorkerPaymentRepository,
        expense_repository: JobWorkExpenseRepository,
        payable_repository: PayableRepository,
    ):
        self.payment_repo = payment_repository
        self.expense_repo = expense_repository
        self.payable_repo = payable_repository

    @property
    def _session(self):
        return self.payment_repo.session

    async def record_payment(
        self, schema: JobWorkerPaymentCreate, created_by: UUID
    ) -> JobWorkerPaymentModel:
        amount = Decimal(str(schema.amount))

        # Validate: payment must not exceed outstanding
        total_exp, total_paid = await self.payable_repo.get_totals_for_worker(
            schema.job_worker_id
        )
        outstanding = total_exp - total_paid

        if amount > outstanding:
            raise ValidationException(
                f"Payment ₹{amount:.2f} exceeds outstanding ₹{outstanding:.2f} for this Job Worker."
            )

        today = date.today()
        prefix = f"PAY-{today.strftime('%d%m%y')}"
        reference = await _next_seq(self._session, prefix)

        payment = JobWorkerPaymentModel(
            reference=reference,
            job_worker_id=schema.job_worker_id,
            payment_date=schema.payment_date,
            amount=amount,
            payment_account=schema.payment_account,
            payment_reference=schema.payment_reference,
            notes=schema.notes,
            status="POSTED",
            created_by=created_by,
            updated_by=created_by,
        )
        await self.payment_repo.create(payment)
        await self._session.flush()  # get payment.id

        # FIFO allocation
        remaining = amount
        expenses = await self.expense_repo.get_unpaid_for_worker(schema.job_worker_id)

        # Compute already-allocated amounts per expense
        from sqlalchemy import func, select as sa_select
        from src.domains.accounting.job_worker.models.payable_allocation import PayableAllocationModel as AllocModel

        for expense in expenses:
            if remaining <= 0:
                break
            alloc_stmt = sa_select(func.coalesce(func.sum(AllocModel.allocated_amount), 0)).where(
                AllocModel.expense_id == expense.id
            )
            alloc_res = await self._session.execute(alloc_stmt)
            already_allocated = Decimal(str(alloc_res.scalar() or 0))
            expense_amount = Decimal(str(expense.amount))
            available_on_expense = expense_amount - already_allocated

            if available_on_expense <= 0:
                continue

            to_allocate = min(remaining, available_on_expense)
            alloc = PayableAllocationModel(
                expense_id=expense.id,
                payment_id=payment.id,
                allocated_amount=to_allocate,
                created_by=created_by,
                updated_by=created_by,
            )
            await self.payment_repo.create_allocation(alloc)
            remaining -= to_allocate

        return payment

    async def get_all_for_worker(self, job_worker_id: UUID) -> List[JobWorkerPaymentModel]:
        return await self.payment_repo.get_all_for_worker(job_worker_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[JobWorkerPaymentModel]:
        return await self.payment_repo.get_all(skip, limit)
