from uuid import UUID
from src.domains.data_ingestion.repositories.import_summary import ImportSummaryRepository
from src.domains.data_ingestion.models.import_summary import ImportSummaryModel
from src.domains.data_ingestion.schemas.import_summary import ImportSummaryCreate

class ImportSummaryService:
    def __init__(self, repository: ImportSummaryRepository):
        self.repository = repository

    async def generate_initial_summary(self, job_id: UUID, total_records: int, created_by: UUID) -> ImportSummaryModel:
        summary = ImportSummaryModel(
            import_job_id=job_id,
            total_records=total_records,
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(summary)

    async def update_summary_stats(self, job_id: UUID, successful: int, failed: int, duplicate: int, updated_by: UUID) -> ImportSummaryModel:
        summary = await self.repository.get_by_job_id(job_id)
        if not summary:
            # Create a zeroed summary if it doesn't exist somehow
            summary = ImportSummaryModel(import_job_id=job_id, created_by=updated_by)
            
        summary.successful_records += successful
        summary.failed_records += failed
        summary.duplicate_records += duplicate
        summary.updated_by = updated_by
        
        if summary.id:
            return await self.repository.update(summary)
        return await self.repository.create(summary)
