from pydantic import BaseModel, Field, UUID4, constr, RootModel
from typing import List, Literal
from datetime import datetime

class PackerEventItem(BaseModel):
    sku: str = Field(..., description="The SKU of the packed item")
    quantity: int = Field(..., gt=0, description="The quantity packed")

class PackerEventPayload(BaseModel):
    event_id: UUID4 = Field(..., description="Unique, immutable identifier for the physical event")
    event_type: Literal["PACKED", "RTO_RECEIVED", "CUSTOMER_RETURN_RECEIVED"] = Field(..., description="The type of event")
    occurred_at: datetime = Field(..., description="When the physical event actually occurred in the warehouse")
    order_id: str = Field(..., description="The commercial ShopDeck Order ID")
    awb: str = Field(..., description="The logistics AWB identifier")
    items: List[PackerEventItem] = Field(..., min_length=1, description="List of items and quantities")

class PackerEventResponse(BaseModel):
    event_id: UUID4
    status: str
