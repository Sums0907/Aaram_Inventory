from uuid import UUID
from datetime import date
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.accounting.job_worker.models.job_work_rate import JobWorkRateModel
from src.domains.accounting.job_worker.schemas.job_work_rate import JobWorkRateCreate


class JobWorkRateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, schema: JobWorkRateCreate, created_by: UUID) -> JobWorkRateModel:
        obj = JobWorkRateModel(
            job_worker_id=schema.job_worker_id,
            sku_id=schema.sku_id,
            rate=Decimal(str(schema.rate)),
            rate_basis=schema.rate_basis,
            effective_from=schema.effective_from,
            is_active=True,
            notes=schema.notes,
            created_by=created_by,
            updated_by=created_by,
        )
        self.session.add(obj)
        return obj

    async def get_applicable_rate(
        self, job_worker_id: UUID, sku_id: UUID, session: Optional[AsyncSession] = None
    ) -> Optional[JobWorkRateModel]:
        """Return the exactly one active rate for this job worker and sku."""
        db = session or self.session
        stmt = (
            select(JobWorkRateModel)
            .where(
                JobWorkRateModel.job_worker_id == job_worker_id,
                JobWorkRateModel.sku_id == sku_id,
                JobWorkRateModel.is_active == True,
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    async def archive_active_rate(self, job_worker_id: UUID, sku_id: UUID, updated_by: UUID) -> None:
        """Atomically archives any active rate for this combination."""
        from sqlalchemy import update
        from src.foundation.utilities.dates import utc_now
        stmt = (
            update(JobWorkRateModel)
            .where(
                JobWorkRateModel.job_worker_id == job_worker_id,
                JobWorkRateModel.sku_id == sku_id,
                JobWorkRateModel.is_active == True,
            )
            .values(is_active=False, updated_by=updated_by, updated_on=utc_now())
        )
        await self.session.execute(stmt)

    async def get_all_for_worker(self, job_worker_id: UUID) -> List[JobWorkRateModel]:
        stmt = (
            select(JobWorkRateModel)
            .where(JobWorkRateModel.job_worker_id == job_worker_id)
            .order_by(JobWorkRateModel.sku_id, JobWorkRateModel.effective_from.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_all(self) -> List[JobWorkRateModel]:
        stmt = select(JobWorkRateModel).order_by(
            JobWorkRateModel.job_worker_id,
            JobWorkRateModel.sku_id,
            JobWorkRateModel.effective_from.desc(),
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_by_id(self, rate_id: UUID) -> Optional[JobWorkRateModel]:
        stmt = select(JobWorkRateModel).where(JobWorkRateModel.id == rate_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()
