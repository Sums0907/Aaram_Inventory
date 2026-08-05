from uuid import UUID
from datetime import datetime
from src.foundation.validation.base import BaseSchema

class MatchRelationshipCreate(BaseSchema):
    match_job_id: UUID
    source_type: str
    source_id: UUID
    target_type: str
    target_id: UUID
    relationship_type: str
    status: str = "MATCHED"

class MatchRelationshipResponse(MatchRelationshipCreate):
    id: UUID
    created_on: datetime
    updated_on: datetime
