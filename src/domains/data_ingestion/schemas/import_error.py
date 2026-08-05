from typing import Optional
from uuid import UUID
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from datetime import datetime

class ImportErrorBase(BaseSchema):
    import_job_id: UUID
    import_record_id: Optional[UUID] = None
    error_code: str = Field(..., max_length=100)
    error_message: str = Field(..., max_length=1000)
    row_number: Optional[int] = None

class ImportErrorCreate(ImportErrorBase):
    pass

class ImportErrorResponse(ImportErrorCreate):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
