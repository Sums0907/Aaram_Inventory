from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Boolean
from src.foundation.database.models import BaseModel

class Supplier(BaseModel):
    __tablename__ = "masters_suppliers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    contact_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_job_worker: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
