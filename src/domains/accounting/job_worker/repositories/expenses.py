from uuid import UUID
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.accounting.job_worker.models.job_work_expense import JobWorkExpenseModel


class JobWorkExpenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj: JobWorkExpenseModel) -> JobWorkExpenseModel:
        self.session.add(obj)
        return obj

    async def exists_for_receipt(self, source_receipt_id: UUID) -> bool:
        """Guard: prevent duplicate expenses for the same receipt."""
        stmt = select(JobWorkExpenseModel.id).where(
            JobWorkExpenseModel.source_receipt_id == source_receipt_id,
            JobWorkExpenseModel.status == "POSTED",
        )
        res = await self.session.execute(stmt)
        return res.scalars().first() is not None

    async def get_all_for_worker(self, job_worker_id: UUID) -> List[JobWorkExpenseModel]:
        stmt = (
            select(JobWorkExpenseModel)
            .where(
                JobWorkExpenseModel.job_worker_id == job_worker_id,
                JobWorkExpenseModel.status == "POSTED",
            )
            .order_by(JobWorkExpenseModel.expense_date.asc(), JobWorkExpenseModel.created_on.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[JobWorkExpenseModel]:
        stmt = (
            select(JobWorkExpenseModel)
            .where(JobWorkExpenseModel.status == "POSTED")
            .order_by(JobWorkExpenseModel.expense_date.desc())
            .offset(skip).limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, expense_id: UUID) -> Optional[JobWorkExpenseModel]:
        stmt = select(JobWorkExpenseModel).where(JobWorkExpenseModel.id == expense_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_unpaid_for_worker(
        self, job_worker_id: UUID
    ) -> List[JobWorkExpenseModel]:
        """Return posted expenses ordered oldest-first for FIFO allocation."""
        stmt = (
            select(JobWorkExpenseModel)
            .where(
                JobWorkExpenseModel.job_worker_id == job_worker_id,
                JobWorkExpenseModel.status == "POSTED",
            )
            .order_by(JobWorkExpenseModel.expense_date.asc(), JobWorkExpenseModel.created_on.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
