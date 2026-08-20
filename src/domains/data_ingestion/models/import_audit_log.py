from datetime import datetime
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from src.foundation.database.models import BaseModel

class ImportAuditLogModel(BaseModel):
    __tablename__ = "import_audit_logs"

    batch_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    environment: Mapped[str] = mapped_column(String(50), nullable=False)
    
    executed_by_user_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False) # DRY_RUN, COMMITTED, FAILED
    rollback_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # NONE, SUCCESS, FAILED
    
    records_processed: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
