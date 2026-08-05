from typing import Optional, List
from uuid import UUID
from pydantic import Field
from datetime import date, datetime
from src.foundation.validation.base import BaseSchema

class SalesOrderItemBase(BaseSchema):
    external_sku_code: str = Field(..., max_length=255)
    sku_id: Optional[UUID] = None
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    tax_amount: float = Field(..., ge=0)

class SalesOrderItemCreate(SalesOrderItemBase):
    pass

class SalesOrderItemResponse(SalesOrderItemBase):
    id: UUID
    order_id: UUID
    created_on: datetime
    updated_on: datetime

class SalesOrderBase(BaseSchema):
    external_order_id: str = Field(..., max_length=255)
    channel: str = Field(..., max_length=100)
    order_date: date
    status: str = Field(..., max_length=100)
    
    customer_name: str = Field(..., max_length=255)
    customer_mobile: Optional[str] = Field(None, max_length=50)
    
    shipping_address: str = Field(..., max_length=1000)
    shipping_pincode: str = Field(..., max_length=20)
    shipping_city: str = Field(..., max_length=100)
    shipping_state: str = Field(..., max_length=100)
    
    payment_method: str = Field(..., max_length=50)
    
    gross_amount: float = Field(..., ge=0)
    discount_amount: float = Field(..., ge=0)
    shipping_fee: float = Field(..., ge=0)
    cod_fee: float = Field(..., ge=0)
    net_amount: float = Field(..., ge=0)

class SalesOrderCreate(SalesOrderBase):
    items: List[SalesOrderItemCreate]

class SalesOrderResponse(SalesOrderBase):
    id: UUID
    items: List[SalesOrderItemResponse]
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
