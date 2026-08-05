from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.data_ingestion.models.import_file import ImportFileModel

class ImportFileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_job_id(self, job_id: UUID) -> Optional[ImportFileModel]:
        result = await self.session.execute(select(ImportFileModel).filter(ImportFileModel.import_job_id == job_id))
        return result.scalars().first()

    async def get_by_md5(self, md5_hash: str) -> Optional[ImportFileModel]:
        result = await self.session.execute(select(ImportFileModel).filter(ImportFileModel.md5_hash == md5_hash))
        return result.scalars().first()

    async def create(self, file_model: ImportFileModel) -> ImportFileModel:
        self.session.add(file_model)
        await self.session.commit()
        await self.session.refresh(file_model)
        return file_model
