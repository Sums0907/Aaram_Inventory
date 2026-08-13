"""
Job Worker Rate Service.

Manages the Rate Master: create rates and look up the applicable rate
for a (job_worker, sku, date) triple using effective-date versioning.
"""
from uuid import UUID
from datetime import date
from typing import List, Optional
from sqlalchemy import select
from src.foundation.database.models import SequenceModel
from src.domains.accounting.job_worker.repositories.rates import JobWorkRateRepository
from src.domains.accounting.job_worker.models.job_work_rate import JobWorkRateModel
from src.domains.accounting.job_worker.schemas.job_work_rate import JobWorkRateCreate
from src.foundation.exceptions.base import ValidationException


class RateService:
    def __init__(
        self, 
        repository: JobWorkRateRepository,
        expense_repository=None
    ):
        self.repository = repository
        self.expense_repository = expense_repository

    async def create_rate(self, schema: JobWorkRateCreate, created_by: UUID) -> JobWorkRateModel:
        if schema.rate <= 0:
            raise ValidationException("Rate must be greater than zero.")
        
        # Atomically archive the current active rate
        await self.repository.archive_active_rate(
            schema.job_worker_id, schema.sku_id, updated_by=created_by
        )
        
        obj = await self.repository.create(schema, created_by)
        await self.repository.session.commit()
        await self.repository.session.refresh(obj)
        return obj

    async def get_applicable_rate(
        self, job_worker_id: UUID, sku_id: UUID
    ) -> Optional[JobWorkRateModel]:
        """Return the active rate or None if not configured."""
        return await self.repository.get_applicable_rate(job_worker_id, sku_id)

    async def get_all_for_worker(self, job_worker_id: UUID) -> List[JobWorkRateModel]:
        return await self.repository.get_all_for_worker(job_worker_id)

    async def get_all(self) -> List[JobWorkRateModel]:
        return await self.repository.get_all()

    async def deactivate_rate(self, rate_id: UUID, updated_by: UUID) -> JobWorkRateModel:
        rate = await self.repository.get_by_id(rate_id)
        if not rate:
            raise ValidationException(f"Rate {rate_id} not found.")
        if not rate.is_active:
            raise ValidationException("Cannot modify an already archived rate.")
            
        if self.expense_repository:
            # Check if this exact rate version was used in any expense
            is_used = await self.expense_repository.exists_by_rate_id(rate_id)
            if is_used:
                raise ValidationException("Cannot delete or deactivate a rate that has already been used. Please revise the rate instead to create a new version.")

        rate.is_active = False
        rate.updated_by = updated_by
        await self.repository.session.commit()
        return rate
