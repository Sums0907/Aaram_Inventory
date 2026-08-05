from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey
from src.foundation.database.models import BaseModel

class ImportFileModel(BaseModel):
    __tablename__ = "import_files"

    import_job_id: Mapped[UUID] = mapped_column(ForeignKey("import_jobs.id"), nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    md5_hash: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
