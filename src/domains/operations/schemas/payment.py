from typing import Optional
from uuid import UUID
from pydantic import Field
from datetime import datetime
from src.foundation.validation.base import BaseSchema

class PaymentCreate(BaseSchema):
    transaction_id: str = Field(..., max_length=255)
    transaction_type: str = Field(..., max_length=100)
    
    order_reference: str = Field(..., max_length=255)
    matched_order_id: Optional[UUID] = None
    
    payment_method: str = Field(..., max_length=100)
    
    gross_amount: float = 0.0
    gateway_fee: float = 0.0
    gateway_tax: float = 0.0
    net_amount: float = 0.0   
    payment_captured_at: Optional[datetime] = None
    
    settlement_id: Optional[UUID] = None
    external_settlement_id: Optional[str] = Field(None, max_length=255)
    utr_number: Optional[str] = Field(None, max_length=255)

class PaymentResponse(PaymentCreate):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
