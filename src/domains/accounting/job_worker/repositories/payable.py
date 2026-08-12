from uuid import UUID
from decimal import Decimal
from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.accounting.job_worker.models.job_work_expense import JobWorkExpenseModel
from src.domains.accounting.job_worker.models.job_worker_payment import JobWorkerPaymentModel


class PayableRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_totals_for_worker(self, job_worker_id: UUID) -> Tuple[Decimal, Decimal]:
        """Return (total_expenses, total_paid) for a given Job Worker."""
        exp_stmt = select(func.coalesce(func.sum(JobWorkExpenseModel.amount), 0)).where(
            JobWorkExpenseModel.job_worker_id == job_worker_id,
            JobWorkExpenseModel.status == "POSTED",
        )
        pay_stmt = select(func.coalesce(func.sum(JobWorkerPaymentModel.amount), 0)).where(
            JobWorkerPaymentModel.job_worker_id == job_worker_id,
            JobWorkerPaymentModel.status == "POSTED",
        )
        exp_res = await self.session.execute(exp_stmt)
        pay_res = await self.session.execute(pay_stmt)
        total_exp = Decimal(str(exp_res.scalar() or 0))
        total_pay = Decimal(str(pay_res.scalar() or 0))
        return total_exp, total_pay

    async def get_global_totals(self) -> Tuple[Decimal, Decimal]:
        """Return (total_expenses, total_paid) across all Job Workers."""
        exp_stmt = select(func.coalesce(func.sum(JobWorkExpenseModel.amount), 0)).where(
            JobWorkExpenseModel.status == "POSTED"
        )
        pay_stmt = select(func.coalesce(func.sum(JobWorkerPaymentModel.amount), 0)).where(
            JobWorkerPaymentModel.status == "POSTED"
        )
        exp_res = await self.session.execute(exp_stmt)
        pay_res = await self.session.execute(pay_stmt)
        return Decimal(str(exp_res.scalar() or 0)), Decimal(str(pay_res.scalar() or 0))

    async def get_worker_ids_with_expenses(self) -> List[UUID]:
        stmt = (
            select(JobWorkExpenseModel.job_worker_id)
            .where(JobWorkExpenseModel.status == "POSTED")
            .distinct()
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
