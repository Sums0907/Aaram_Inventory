import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class ImportAction(Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    IGNORED = "IGNORED"
    FAILED = "FAILED"
    AMBIGUOUS = "AMBIGUOUS"

@dataclass
class ImportRowResult:
    row_index: int
    action: ImportAction
    entity_id: Optional[str] = None
    identifier: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    details: List[str] = field(default_factory=list)

@dataclass
class ImportResult:
    entity_type: str
    total_records: int = 0
    created_count: int = 0
    updated_count: int = 0
    ignored_count: int = 0
    failed_count: int = 0
    ambiguous_count: int = 0
    row_results: List[ImportRowResult] = field(default_factory=list)
    global_errors: List[str] = field(default_factory=list)
    
    @property
    def is_successful(self) -> bool:
        return self.failed_count == 0 and self.ambiguous_count == 0 and len(self.global_errors) == 0

class BaseMasterDataImporter:
    """Base class for identity-based master data import operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def import_data(self, data: List[Dict[str, Any]], is_dry_run: bool = True) -> ImportResult:
        raise NotImplementedError("Subclasses must implement import_data")
