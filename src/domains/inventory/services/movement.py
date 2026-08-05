from uuid import UUID
from datetime import datetime, timezone
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.foundation.exceptions.base import ValidationException

class InventoryMovementService:
    def __init__(self, repository: InventoryMovementRepository):
        self.repository = repository
        
    async def create_movement(self, schema: InventoryMovementCreate, user_id: UUID):
        existing = await self.repository.get_by_movement_number(schema.movement_number)
        if existing:
            raise ValidationException(f"Movement with number {schema.movement_number} already exists")
            
        return await self.repository.create_movement(schema, user_id)
        
    async def get_balance(self, warehouse_id: UUID, sku_id: UUID) -> int:
        return await self.repository.get_balance(warehouse_id, sku_id)
