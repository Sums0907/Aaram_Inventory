from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from src.domains.data_ingestion.repositories.import_job import ImportJobRepository
from src.domains.data_ingestion.models.import_job import ImportJobModel
from src.domains.data_ingestion.schemas.import_job import ImportJobCreate, ImportJobUpdate
from src.foundation.exceptions.base import NotFoundException

class ImportJobService:
    def __init__(self, repository: ImportJobRepository):
        self.repository = repository

    async def get_job(self, job_id: UUID) -> ImportJobModel:
        job = await self.repository.get_by_id(job_id)
        if not job:
            raise NotFoundException(message="Import Job not found")
        return job

    async def list_jobs(self, skip: int = 0, limit: int = 100) -> List[ImportJobModel]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create_job(self, schema: ImportJobCreate, created_by: UUID) -> ImportJobModel:
        job = ImportJobModel(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(job)

    async def update_job_status(self, job_id: UUID, status: str, updated_by: UUID) -> ImportJobModel:
        job = await self.get_job(job_id)
        job.status = status
        
        if status == "PROCESSING" and not job.started_at:
            job.started_at = datetime.now(timezone.utc)
        elif status in ["COMPLETED", "FAILED", "PARTIAL_SUCCESS"]:
            job.finished_at = datetime.now(timezone.utc)
            
        job.updated_by = updated_by
        return await self.repository.update(job)
