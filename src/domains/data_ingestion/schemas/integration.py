from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import Field
from src.foundation.validation.base import BaseSchema
from src.foundation.enums.status import GenericStatus

class IntegrationBase(BaseSchema):
    integration_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    integration_type: str = Field(..., max_length=50, description="e.g. MARKETPLACE, ACCOUNTING")

class IntegrationCreate(IntegrationBase):
    integration_code: str = Field(..., min_length=1, max_length=50)

class IntegrationUpdate(IntegrationBase):
    pass

class IntegrationResponse(IntegrationCreate):
    id: UUID
    status: GenericStatus
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
