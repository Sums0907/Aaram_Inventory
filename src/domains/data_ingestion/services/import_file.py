from uuid import UUID
from src.domains.data_ingestion.repositories.import_file import ImportFileRepository
from src.domains.data_ingestion.models.import_file import ImportFileModel
from src.domains.data_ingestion.schemas.import_file import ImportFileCreate
from src.foundation.exceptions.base import NotFoundException, ValidationException

class ImportFileService:
    def __init__(self, repository: ImportFileRepository):
        self.repository = repository

    async def get_by_job_id(self, job_id: UUID) -> ImportFileModel:
        file_model = await self.repository.get_by_job_id(job_id)
        if not file_model:
            raise NotFoundException(message="Import File not found for this job")
        return file_model

    async def create_file_record(self, schema: ImportFileCreate, created_by: UUID) -> ImportFileModel:
        existing = await self.repository.get_by_md5(schema.md5_hash)
        if existing:
            raise ValidationException(message="A file with this MD5 hash has already been processed.")
            
        file_model = ImportFileModel(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(file_model)
