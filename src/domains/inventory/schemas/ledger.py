from typing import List, Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel
from src.domains.inventory.schemas.movement import InventoryMovementResponse

class InventoryLedgerEntry(BaseModel):
    movement: InventoryMovementResponse
    running_balance: int

class InventoryLedgerResponse(BaseModel):
    sku_id: UUID
    opening_balance: int
    entries: List[InventoryLedgerEntry]
    closing_balance: int
    generated_at: date
