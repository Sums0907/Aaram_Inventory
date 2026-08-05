from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.data_ingestion.models.import_summary import ImportSummaryModel

class ImportSummaryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_job_id(self, job_id: UUID) -> Optional[ImportSummaryModel]:
        result = await self.session.execute(select(ImportSummaryModel).filter(ImportSummaryModel.import_job_id == job_id))
        return result.scalars().first()

    async def create(self, summary_model: ImportSummaryModel) -> ImportSummaryModel:
        self.session.add(summary_model)
        await self.session.commit()
        await self.session.refresh(summary_model)
        return summary_model

    async def update(self, summary_model: ImportSummaryModel) -> ImportSummaryModel:
        await self.session.commit()
        await self.session.refresh(summary_model)
        return summary_model
