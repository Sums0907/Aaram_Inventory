from typing import Optional, List
from uuid import UUID
from pydantic import Field
from datetime import date, datetime
from src.foundation.validation.base import BaseSchema

class TaxInvoiceItemBase(BaseSchema):
    external_sku_code: str = Field(..., max_length=255)
    sku_id: Optional[UUID] = None
    hsn_code: str = Field(..., max_length=50)
    
    base_price: float = Field(..., ge=0)
    tax_percent: float = Field(..., ge=0)
    igst: float = Field(..., ge=0)
    cgst: float = Field(..., ge=0)
    sgst: float = Field(..., ge=0)
    selling_price: float = Field(..., ge=0)

class TaxInvoiceItemCreate(TaxInvoiceItemBase):
    pass

class TaxInvoiceItemResponse(TaxInvoiceItemBase):
    id: UUID
    invoice_id: UUID
    created_on: datetime
    updated_on: datetime

class TaxInvoiceBase(BaseSchema):
    invoice_no: str = Field(..., max_length=255)
    external_order_id: str = Field(..., max_length=255)
    order_id: Optional[UUID] = None
    
    document_type: str = Field(..., max_length=100)
    invoice_date: date
    customer_state: str = Field(..., max_length=100)
    
    total_base_price: float = Field(..., ge=0)
    total_tax: float = Field(..., ge=0)
    total_igst: float = Field(..., ge=0)
    total_cgst: float = Field(..., ge=0)
    total_sgst: float = Field(..., ge=0)

class TaxInvoiceCreate(TaxInvoiceBase):
    items: List[TaxInvoiceItemCreate]

class TaxInvoiceResponse(TaxInvoiceBase):
    id: UUID
    items: List[TaxInvoiceItemResponse]
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
