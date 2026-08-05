from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.data_ingestion.models.import_job import ImportJobModel

class ImportJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, job_id: UUID) -> Optional[ImportJobModel]:
        result = await self.session.execute(select(ImportJobModel).filter(ImportJobModel.id == job_id))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ImportJobModel]:
        result = await self.session.execute(select(ImportJobModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, job: ImportJobModel) -> ImportJobModel:
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def update(self, job: ImportJobModel) -> ImportJobModel:
        await self.session.commit()
        await self.session.refresh(job)
        return job
