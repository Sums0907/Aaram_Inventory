from uuid import UUID
from datetime import datetime, timezone
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.schemas.ledger import InventoryLedgerResponse, InventoryLedgerEntry
from src.domains.inventory.schemas.movement import InventoryMovementResponse

class InventoryLedgerService:
    def __init__(self, movement_repository: InventoryMovementRepository):
        self.movement_repository = movement_repository
        
    async def generate_ledger(self, sku_id: UUID) -> InventoryLedgerResponse:
        """
        Dynamically reconstructs the complete stock history of a SKU chronologically 
        from its movements, calculating the running Closing Stock.
        """
        movements = await self.movement_repository.get_movements_for_sku(sku_id)
        
        entries = []
        running_balance = 0
        
        for movement in movements:
            running_balance += movement.quantity
            
            # Convert DB model to Response Schema
            # Pydantic model_validate works well for ORM instances with from_attributes=True,
            # but since we didn't specify Config.from_attributes in base, we'll manually cast or use dict.
            movement_schema = InventoryMovementResponse(
                id=movement.id,
                created_on=movement.created_on,
                updated_on=movement.updated_on,
                created_by=movement.created_by,
                updated_by=movement.updated_by,
                movement_number=movement.movement_number,
                movement_type=movement.movement_type,
                movement_date=movement.movement_date,
                posting_date=movement.posting_date,
                status=movement.status,
                warehouse_id=movement.warehouse_id,
                sku_id=movement.sku_id,
                quantity=movement.quantity,
                unit_cost=float(movement.unit_cost),
                reference_type=movement.reference_type,
                reference_number=movement.reference_number,
                reference_id=movement.reference_id
            )
            
            entry = InventoryLedgerEntry(
                movement=movement_schema,
                running_balance=running_balance
            )
            entries.append(entry)
            
        return InventoryLedgerResponse(
            sku_id=sku_id,
            opening_balance=0,
            entries=entries,
            closing_balance=running_balance,
            generated_at=datetime.now(timezone.utc).date()
        )
