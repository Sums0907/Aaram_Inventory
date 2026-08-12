from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.accounting.job_worker.models.job_worker_payment import JobWorkerPaymentModel
from src.domains.accounting.job_worker.models.payable_allocation import PayableAllocationModel


class JobWorkerPaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj: JobWorkerPaymentModel) -> JobWorkerPaymentModel:
        self.session.add(obj)
        return obj

    async def create_allocation(self, obj: PayableAllocationModel) -> PayableAllocationModel:
        self.session.add(obj)
        return obj

    async def get_all_for_worker(self, job_worker_id: UUID) -> List[JobWorkerPaymentModel]:
        stmt = (
            select(JobWorkerPaymentModel)
            .where(
                JobWorkerPaymentModel.job_worker_id == job_worker_id,
                JobWorkerPaymentModel.status == "POSTED",
            )
            .order_by(JobWorkerPaymentModel.payment_date.asc(), JobWorkerPaymentModel.created_on.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[JobWorkerPaymentModel]:
        stmt = (
            select(JobWorkerPaymentModel)
            .where(JobWorkerPaymentModel.status == "POSTED")
            .order_by(JobWorkerPaymentModel.payment_date.desc())
            .offset(skip).limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, payment_id: UUID) -> Optional[JobWorkerPaymentModel]:
        stmt = select(JobWorkerPaymentModel).where(JobWorkerPaymentModel.id == payment_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()
