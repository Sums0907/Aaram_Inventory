import uuid
from typing import List
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Uuid, ForeignKey, Integer, Text
from src.foundation.database.models import BaseModel

class PurchaseReturn(BaseModel):
    __tablename__ = "inventory_purchase_returns"

    return_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    supplier_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("masters_suppliers.id"), nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    reference_grn: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="RETURNED")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[List["PurchaseReturnItem"]] = relationship("PurchaseReturnItem", back_populates="purchase_return", cascade="all, delete-orphan")

class PurchaseReturnItem(BaseModel):
    __tablename__ = "inventory_purchase_return_items"

    return_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("inventory_purchase_returns.id"), nullable=False)
    sku_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("skus.id"), nullable=False)
    
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_of_measure: Mapped[str | None] = mapped_column(String(50), nullable=True)

    purchase_return: Mapped["PurchaseReturn"] = relationship("PurchaseReturn", back_populates="items")
