from typing import Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Numeric, ForeignKey
from src.foundation.database.models import BaseModel

class InventoryMovementModel(BaseModel):
    __tablename__ = "inventory_movements"

    movement_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    movement_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. SALES_FULFILLMENT, STOCK_ADJUSTMENT, RETURN
    movement_date: Mapped[date] = mapped_column(Date, nullable=False)
    posting_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="POSTED") # DRAFT, POSTED, CANCELLED

    warehouse_id: Mapped[UUID] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    sku_id: Mapped[UUID] = mapped_column(ForeignKey("skus.id"), nullable=False, index=True)
    
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False) # positive for IN, negative for OUT
    unit_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    
    reference_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. SALES_ORDER
    reference_number: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
