from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.data_ingestion.models.import_error import ImportErrorModel

class ImportErrorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_job_id(self, job_id: UUID) -> List[ImportErrorModel]:
        result = await self.session.execute(select(ImportErrorModel).filter(ImportErrorModel.import_job_id == job_id))
        return list(result.scalars().all())

    async def create(self, error_model: ImportErrorModel) -> ImportErrorModel:
        self.session.add(error_model)
        await self.session.commit()
        await self.session.refresh(error_model)
        return error_model
        
    async def create_batch(self, errors: List[ImportErrorModel]) -> None:
        self.session.add_all(errors)
        await self.session.commit()
