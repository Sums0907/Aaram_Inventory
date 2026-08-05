from typing import Optional
from uuid import UUID
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from datetime import datetime

class ImportSummaryBase(BaseSchema):
    import_job_id: UUID
    total_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    duplicate_records: int = 0

class ImportSummaryCreate(ImportSummaryBase):
    pass

class ImportSummaryResponse(ImportSummaryCreate):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
