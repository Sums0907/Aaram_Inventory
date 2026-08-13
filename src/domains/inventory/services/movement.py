from uuid import UUID
from datetime import datetime, timezone, date
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.foundation.exceptions.base import ValidationException

from src.domains.inventory.services.balance_calculator import BalanceCalculatorService

class InventoryMovementService:
    def __init__(self, repository: InventoryMovementRepository, balance_calculator: BalanceCalculatorService):
        self.repository = repository
        self.balance_calculator = balance_calculator
        
    async def create_movement(self, schema: InventoryMovementCreate, user_id: UUID, session=None):
        existing = await self.repository.get_by_movement_number(schema.movement_number, session=session)
        if existing:
            raise ValidationException(f"Movement with number {schema.movement_number} already exists")
            
        movement = await self.repository.create_movement(schema, user_id, session=session)
        
        # Calculate new balance
        await self.balance_calculator.recalculate_balance(
            warehouse_id=movement.warehouse_id, 
            sku_id=movement.sku_id,
            session=session
        )
        
        return movement
        
    async def get_balance(self, warehouse_id: UUID, sku_id: UUID) -> int:
        return await self.repository.get_balance(warehouse_id, sku_id)

    def _map_activity_name(self, movement_type: str) -> str:
        mapping = {
            "PURCHASE_RECEIPT": "Goods Received",
            "SALES_FULFILLMENT": "Daily Sales",
            "CUSTOMER_RETURN": "Sales Return",
            "MANUAL_ADJUSTMENT": "Manual Adjustment",
            "STOCK_COUNT_ADJUSTMENT": "Stock Correction",
            "JOB_WORK_ISSUE": "Job Work Issue",
            "JOB_WORK_RECEIPT": "Job Work Receipt",
            "OPENING_STOCK": "Opening Stock",
            "PURCHASE_RETURN": "Purchase Return",
            "RTO_RETURN": "Courier Return"
        }
        return mapping.get(movement_type, movement_type)

    async def get_activities(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        movement_type: str = None, 
        sku_id: UUID = None,
        item_type: str = None,
        date_from: date = None,
        date_to: date = None
    ):
        from src.domains.inventory.schemas.activity import ActivityResponse, InventoryItemResponse, ActivityReference, ActivityListResponse
        
        count = await self.repository.get_activities_count(movement_type, sku_id, item_type, date_from, date_to)
        if count == 0:
            return ActivityListResponse(total_count=0, items=[])
            
        rows = await self.repository.get_activities(skip, limit, movement_type, sku_id, item_type, date_from, date_to)
        
        items = []
        for row in rows:
            # Note: row is a SQLAlchemy mapping, accessing by column name string
            item_resp = InventoryItemResponse(
                id=row["sku_id"],
                name=row["item_name"],
                inventory_code=row["inventory_code"],
                type=row["item_type"].value if hasattr(row["item_type"], "value") else str(row["item_type"])
            )
            
            ref_resp = ActivityReference(
                type=row["reference_type"],
                number=row["reference_number"],
                id=row["reference_id"]
            )
            
            act = ActivityResponse(
                id=row["id"],
                activity_type=row["movement_type"],
                activity_name=self._map_activity_name(row["movement_type"]),
                date=row["movement_date"],
                inventory_item=item_resp,
                quantity=row["quantity"],
                balance_after_activity=row["balance_after_activity"],
                reference=ref_resp,
                remarks=None, # Add to model if needed
                created_on=row["created_on"]
            )
            items.append(act)
            
        return ActivityListResponse(total_count=count, items=items)
