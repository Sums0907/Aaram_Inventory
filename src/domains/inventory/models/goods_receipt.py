import uuid
from typing import List
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric, String, Date, Uuid, ForeignKey, Integer, Text
from src.foundation.database.models import BaseModel

class GoodsReceipt(BaseModel):
    __tablename__ = "inventory_goods_receipts"

    grn_number: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    supplier_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("masters_suppliers.id"), nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
    receipt_type: Mapped[str] = mapped_column(String(50), nullable=False, default="RAW_MATERIAL_RECEIPT")
    
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False)
    invoice_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    challan_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="RECEIVED")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[List["GoodsReceiptItem"]] = relationship("GoodsReceiptItem", back_populates="goods_receipt", cascade="all, delete-orphan")

class GoodsReceiptItem(BaseModel):
    __tablename__ = "inventory_goods_receipt_items"

    grn_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("inventory_goods_receipts.id"), nullable=False)
    sku_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("skus.id"), nullable=False)
    
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    unit_of_measure: Mapped[str | None] = mapped_column(String(50), nullable=True)

    goods_receipt: Mapped["GoodsReceipt"] = relationship("GoodsReceipt", back_populates="items")
