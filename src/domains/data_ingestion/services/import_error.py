from typing import List
from uuid import UUID
from src.domains.data_ingestion.repositories.import_error import ImportErrorRepository
from src.domains.data_ingestion.models.import_error import ImportErrorModel
from src.domains.data_ingestion.schemas.import_error import ImportErrorCreate

class ImportErrorService:
    def __init__(self, repository: ImportErrorRepository):
        self.repository = repository

    async def get_errors_for_job(self, job_id: UUID) -> List[ImportErrorModel]:
        return await self.repository.get_by_job_id(job_id)

    async def log_errors_batch(self, schemas: List[ImportErrorCreate], created_by: UUID) -> None:
        errors = [
            ImportErrorModel(
                **schema.model_dump(),
                created_by=created_by,
                updated_by=created_by
            )
            for schema in schemas
        ]
        await self.repository.create_batch(errors)
