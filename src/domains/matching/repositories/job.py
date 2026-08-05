from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.matching.models.job import MatchJobModel

class MatchJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, job_id: UUID) -> Optional[MatchJobModel]:
        result = await self.session.execute(
            select(MatchJobModel).filter(MatchJobModel.id == job_id)
        )
        return result.scalars().first()

    async def create(self, job: MatchJobModel) -> MatchJobModel:
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def update(self, job: MatchJobModel) -> MatchJobModel:
        await self.session.commit()
        await self.session.refresh(job)
        return job
