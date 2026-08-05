from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.data_ingestion.models.import_record import ImportRecordModel

class ImportRecordRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_job_id(self, job_id: UUID, skip: int = 0, limit: int = 100) -> List[ImportRecordModel]:
        result = await self.session.execute(
            select(ImportRecordModel).filter(ImportRecordModel.import_job_id == job_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
        
    async def get_by_status(self, job_id: UUID, status: str, skip: int = 0, limit: int = 100) -> List[ImportRecordModel]:
        result = await self.session.execute(
            select(ImportRecordModel)
            .filter(ImportRecordModel.import_job_id == job_id, ImportRecordModel.status == status)
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create_batch(self, records: List[ImportRecordModel]) -> None:
        self.session.add_all(records)
        await self.session.commit()

    async def update(self, record: ImportRecordModel) -> ImportRecordModel:
        await self.session.commit()
        await self.session.refresh(record)
        return record
