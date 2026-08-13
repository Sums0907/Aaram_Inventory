from typing import Optional, Dict
from pydantic import BaseModel, Field
from src.foundation.enums import ItemType
from uuid import UUID

class InventoryItemCreate(BaseModel):
    # Classification
    item_type: ItemType = Field(..., description="Type of inventory item")
    category_id: Optional[UUID] = Field(None, description="Existing Category ID")
    new_category_name: Optional[str] = Field(None, description="Name of new category to create")
    
    # Master Item
    product_id: Optional[UUID] = Field(None, description="Existing Master Item ID")
    new_product_name: Optional[str] = Field(None, description="Name of new Master Item to create")
    
    # Variant / SKU
    item_code: str = Field(..., min_length=1, max_length=50, description="Internal Item Code")
    sku_code: Optional[str] = Field(None, max_length=50, description="SKU Code (Finished Goods only)")
    size: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=255)
    pattern: Optional[str] = Field(None, max_length=255)
    material: Optional[str] = Field(None, max_length=255)
    thread_count: Optional[str] = Field(None, max_length=50)
    attribute_values: Dict[str, str] = Field(default_factory=dict, description="Dynamic variant attributes")
    barcode: Optional[str] = Field(None, max_length=100)
    uom_id: Optional[UUID] = Field(None, description="Authoritative Unit of Measure for components")
