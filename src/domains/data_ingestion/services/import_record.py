from typing import List, Dict, Any
from uuid import UUID
from src.domains.data_ingestion.repositories.import_record import ImportRecordRepository
from src.domains.data_ingestion.models.import_record import ImportRecordModel
from src.domains.data_ingestion.schemas.import_record import ImportRecordCreate
from src.foundation.exceptions.base import NotFoundException

class ImportRecordService:
    def __init__(self, repository: ImportRecordRepository):
        self.repository = repository

    async def get_records_by_job(self, job_id: UUID, skip: int = 0, limit: int = 100) -> List[ImportRecordModel]:
        return await self.repository.get_by_job_id(job_id, skip=skip, limit=limit)

    async def create_records_batch(self, schemas: List[ImportRecordCreate], created_by: UUID) -> None:
        records = [
            ImportRecordModel(
                **schema.model_dump(),
                created_by=created_by,
                updated_by=created_by
            )
            for schema in schemas
        ]
        await self.repository.create_batch(records)

    async def mark_record_valid(self, record: ImportRecordModel, normalized_data: Dict[str, Any], updated_by: UUID) -> ImportRecordModel:
        record.status = "VALID"
        record.normalized_data = normalized_data
        record.updated_by = updated_by
        return await self.repository.update(record)

    async def mark_record_invalid(self, record: ImportRecordModel, updated_by: UUID) -> ImportRecordModel:
        record.status = "INVALID"
        record.updated_by = updated_by
        return await self.repository.update(record)
