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
    def __init__(self, repository: JobWorkRateRepository):
        self.repository = repository

    async def create_rate(self, schema: JobWorkRateCreate, created_by: UUID) -> JobWorkRateModel:
        if schema.rate <= 0:
            raise ValidationException("Rate must be greater than zero.")
        obj = await self.repository.create(schema, created_by)
        return obj

    async def get_applicable_rate(
        self, job_worker_id: UUID, sku_id: UUID, on_date: date
    ) -> Optional[JobWorkRateModel]:
        """Return the effective rate or None if not configured."""
        return await self.repository.get_applicable_rate(job_worker_id, sku_id, on_date)

    async def get_all_for_worker(self, job_worker_id: UUID) -> List[JobWorkRateModel]:
        return await self.repository.get_all_for_worker(job_worker_id)

    async def get_all(self) -> List[JobWorkRateModel]:
        return await self.repository.get_all()

    async def deactivate_rate(self, rate_id: UUID, updated_by: UUID) -> JobWorkRateModel:
        rate = await self.repository.get_by_id(rate_id)
        if not rate:
            raise ValidationException(f"Rate {rate_id} not found.")
        rate.is_active = False
        rate.updated_by = updated_by
        return rate
