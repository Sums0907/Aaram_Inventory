from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from datetime import datetime

class ImportRecordBase(BaseSchema):
    import_job_id: UUID
    record_type: str = Field(..., max_length=50)
    raw_data: Dict[str, Any]
    normalized_data: Optional[Dict[str, Any]] = None

class ImportRecordCreate(ImportRecordBase):
    status: str = Field("PENDING", max_length=50)

class ImportRecordUpdate(BaseSchema):
    status: Optional[str] = Field(None, max_length=50)
    normalized_data: Optional[Dict[str, Any]] = None

class ImportRecordResponse(ImportRecordCreate):
    id: UUID
    normalized_data: Optional[Dict[str, Any]]
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
