from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, Numeric, ForeignKey
from src.foundation.database.models import BaseModel

class TaxInvoiceModel(BaseModel):
    __tablename__ = "operations_tax_invoices"

    invoice_no: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    order_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("operations_sales_orders.id"), nullable=True, index=True) # Link to SalesOrder
    external_order_id: Mapped[str] = mapped_column(String(255), nullable=False) # Fallback reference
    
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    customer_state: Mapped[str] = mapped_column(String(100), nullable=False)
    
    total_base_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    total_tax: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    total_igst: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    total_cgst: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    total_sgst: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    
    items: Mapped[List["TaxInvoiceItemModel"]] = relationship("TaxInvoiceItemModel", back_populates="invoice", cascade="all, delete-orphan")
    order: Mapped[Optional["SalesOrderModel"]] = relationship("SalesOrderModel", back_populates="invoices")

class TaxInvoiceItemModel(BaseModel):
    __tablename__ = "operations_tax_invoice_items"
    
    invoice_id: Mapped[UUID] = mapped_column(ForeignKey("operations_tax_invoices.id"), nullable=False, index=True)
    sku_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("skus.id"), nullable=True) # Nullable for V1 parsing
    external_sku_code: Mapped[str] = mapped_column(String(255), nullable=False)
    hsn_code: Mapped[str] = mapped_column(String(50), nullable=False)
    
    base_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    tax_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    igst: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    cgst: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    sgst: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0.0)
    selling_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    
    invoice: Mapped["TaxInvoiceModel"] = relationship("TaxInvoiceModel", back_populates="items")
