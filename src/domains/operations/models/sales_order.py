from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Numeric, ForeignKey
from src.foundation.database.models import BaseModel

class SalesOrderModel(BaseModel):
    __tablename__ = "operations_sales_orders"

    external_order_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(100), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_mobile: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    shipping_address: Mapped[str] = mapped_column(String(1000), nullable=False)
    shipping_pincode: Mapped[str] = mapped_column(String(20), nullable=False)
    shipping_city: Mapped[str] = mapped_column(String(100), nullable=False)
    shipping_state: Mapped[str] = mapped_column(String(100), nullable=False)
    
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    
    gross_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    shipping_fee: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    cod_fee: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    net_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    
    items: Mapped[List["SalesOrderItemModel"]] = relationship("SalesOrderItemModel", back_populates="order", cascade="all, delete-orphan")
    invoices: Mapped[List["TaxInvoiceModel"]] = relationship("TaxInvoiceModel", back_populates="order")

class SalesOrderItemModel(BaseModel):
    __tablename__ = "operations_sales_order_items"
    
    order_id: Mapped[UUID] = mapped_column(ForeignKey("operations_sales_orders.id"), nullable=False, index=True)
    sku_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("skus.id"), nullable=True) # Nullable for V1 parsing before matching
    external_sku_code: Mapped[str] = mapped_column(String(255), nullable=False)
    
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    
    order: Mapped["SalesOrderModel"] = relationship("SalesOrderModel", back_populates="items")
