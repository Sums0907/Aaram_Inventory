import uuid
from typing import List, Tuple
from datetime import datetime, timezone
from src.domains.inventory.repositories.purchase_return import PurchaseReturnRepository
from src.domains.inventory.models.purchase_return import PurchaseReturn, PurchaseReturnItem
from src.domains.inventory.schemas.purchase_return import PurchaseReturnCreate
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.foundation.exceptions.base import ValidationException

class PurchaseReturnService:
    def __init__(self, repository: PurchaseReturnRepository, movement_service: InventoryMovementService):
        self.repository = repository
        self.movement_service = movement_service

    async def get_by_id(self, return_id: uuid.UUID) -> PurchaseReturn:
        doc = await self.repository.get_by_id(return_id)
        if not doc:
            raise ValidationException(message="Purchase Return not found")
        return doc

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[PurchaseReturn], int]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, schema: PurchaseReturnCreate, created_by: uuid.UUID) -> PurchaseReturn:
        existing = await self.repository.get_by_return_number(schema.return_number)
        if existing:
            raise ValidationException(message=f"Return number {schema.return_number} already exists")

        # 1. Create the Purchase Return document
        doc = PurchaseReturn(
            return_number=schema.return_number,
            supplier_id=schema.supplier_id,
            warehouse_id=schema.warehouse_id,
            return_date=schema.return_date,
            reference_grn=schema.reference_grn,
            remarks=schema.remarks,
            status="RETURNED",
            created_by=created_by,
            updated_by=created_by
        )
        
        items = []
        for item_schema in schema.items:
            item = PurchaseReturnItem(
                sku_id=item_schema.sku_id,
                quantity=item_schema.quantity,
                unit_of_measure=item_schema.unit_of_measure,
                created_by=created_by,
                updated_by=created_by
            )
            items.append(item)
            
        doc.items = items
        saved_doc = await self.repository.create(doc)

        # 2. Trigger Inventory Movements for each returned item
        today = datetime.now(timezone.utc).date()
        for i, item in enumerate(saved_doc.items):
            movement_request = InventoryMovementCreate(
                movement_number=f"MOV-PRT-{saved_doc.return_number}-{i+1}",
                movement_type="PURCHASE_RETURN",
                movement_date=saved_doc.return_date,
                posting_date=today,
                status="POSTED",
                warehouse_id=saved_doc.warehouse_id,
                sku_id=item.sku_id,
                quantity=item.quantity,
                unit_cost=0.0,
                reference_type="VENDOR",
                reference_number=saved_doc.return_number,
                reference_id=saved_doc.supplier_id
            )
            await self.movement_service.create_movement(movement_request, created_by)

        return saved_doc
