from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from src.foundation.database.models import BaseModel

class ImportRecordModel(BaseModel):
    __tablename__ = "import_records"

    import_job_id: Mapped[UUID] = mapped_column(ForeignKey("import_jobs.id"), nullable=False, index=True)
    record_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., SALES_ORDER, SETTLEMENT
    
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    normalized_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING") # PENDING, VALID, INVALID, COMMITTED
