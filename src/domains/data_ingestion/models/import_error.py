from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey
from src.foundation.database.models import BaseModel

class ImportErrorModel(BaseModel):
    __tablename__ = "import_errors"

    import_job_id: Mapped[UUID] = mapped_column(ForeignKey("import_jobs.id"), nullable=False, index=True)
    import_record_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("import_records.id"), nullable=True, index=True)
    
    error_code: Mapped[str] = mapped_column(String(100), nullable=False)
    error_message: Mapped[str] = mapped_column(String(1000), nullable=False)
    row_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
