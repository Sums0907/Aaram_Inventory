from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, String, Integer, DateTime, ForeignKey
from src.foundation.database.models import BaseModel

class InventoryExceptionModel(BaseModel):
    __tablename__ = "inventory_exceptions"

    exception_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    sku_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    
    exception_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_system: Mapped[str] = mapped_column(String(100), nullable=False) # ACCOUNTING, MARKETPLACE, PHYSICAL
    
    expected_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    actual_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    difference: Mapped[int] = mapped_column(Integer, nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN") # OPEN, INVESTIGATING, RESOLVED
    resolution_notes: Mapped[str] = mapped_column(String, nullable=True)
