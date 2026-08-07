from typing import Optional, Literal
from uuid import UUID
from pydantic import Field
from datetime import date, datetime
from src.foundation.validation.base import BaseSchema

MovementType = Literal[
    "OPENING_STOCK",
    "PURCHASE_RECEIPT",
    "PURCHASE_RETURN",
    "SALES_FULFILLMENT",
    "CUSTOMER_RETURN",
    "RTO_RETURN",
    "MANUAL_ADJUSTMENT",
    "STOCK_COUNT_ADJUSTMENT"
]

class InventoryMovementBase(BaseSchema):
    movement_number: str = Field(..., max_length=255)
    movement_type: MovementType
    movement_date: date
    posting_date: date
    status: str = Field(..., max_length=50)

    warehouse_id: UUID
    sku_id: UUID
    
    quantity: int
    unit_cost: float = Field(default=0.0)
    
    reference_type: str = Field(..., max_length=100)
    reference_number: str = Field(..., max_length=255)
    reference_id: UUID

class InventoryMovementCreate(InventoryMovementBase):
    pass

class InventoryMovementResponse(InventoryMovementBase):
    id: UUID
    created_on: datetime
    updated_on: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

# Specific API Request Schemas
class PurchaseReceiptRequest(BaseSchema):
    warehouse_id: UUID
    sku_id: UUID
    quantity: int = Field(..., gt=0, description="Quantity received")
    vendor_id: UUID
    purchase_document: str = Field(..., max_length=255, description="PO Number or Bill Number")
    receipt_date: date

class PurchaseReturnRequest(BaseSchema):
    warehouse_id: UUID
    sku_id: UUID
    quantity: int = Field(..., gt=0, description="Quantity returned")
    vendor_id: UUID
    purchase_document: str = Field(..., max_length=255, description="PO Number or Bill Number")
    return_date: date

class CustomerReturnRequest(BaseSchema):
    warehouse_id: UUID
    sku_id: UUID
    quantity: int = Field(..., gt=0, description="Quantity returned by customer")
    customer_id: UUID
    order_number: str = Field(..., max_length=255, description="Original Order Number")
    return_date: date

class RTOReturnRequest(BaseSchema):
    warehouse_id: UUID
    sku_id: UUID
    quantity: int = Field(..., gt=0, description="Quantity returned by courier (RTO)")
    courier_id: UUID
    awb_number: str = Field(..., max_length=255, description="Tracking AWB Number")
    rto_date: date

class ManualAdjustmentRequest(BaseSchema):
    warehouse_id: UUID
    sku_id: UUID
    quantity: int = Field(..., description="Adjustment quantity (can be positive or negative)")
    reason: str = Field(..., max_length=255)
    reference_number: str = Field(..., max_length=255)
    adjustment_date: date

class StockCountAdjustmentRequest(BaseSchema):
    warehouse_id: UUID
    sku_id: UUID
    system_quantity: int
    physical_count: int
    difference: int = Field(..., description="Calculated difference: physical_count - system_quantity")
    stock_count_reference: str = Field(..., max_length=255)
    count_date: date

