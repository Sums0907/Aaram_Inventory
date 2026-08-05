from typing import Optional
from uuid import UUID
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from datetime import datetime

class ImportFileBase(BaseSchema):
    import_job_id: UUID
    file_name: str = Field(..., max_length=255)
    file_size_bytes: int
    mime_type: str = Field(..., max_length=100)
    md5_hash: str = Field(..., max_length=32)

class ImportFileCreate(ImportFileBase):
    storage_path: Optional[str] = Field(None, max_length=500)

class ImportFileResponse(ImportFileCreate):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
