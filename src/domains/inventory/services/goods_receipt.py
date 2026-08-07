import uuid
from typing import List, Tuple
from datetime import datetime, timezone
from src.domains.inventory.repositories.goods_receipt import GoodsReceiptRepository
from src.domains.inventory.models.goods_receipt import GoodsReceipt, GoodsReceiptItem
from src.domains.inventory.schemas.goods_receipt import GoodsReceiptCreate
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.foundation.exceptions.base import ValidationException

class GoodsReceiptService:
    def __init__(self, repository: GoodsReceiptRepository, movement_service: InventoryMovementService):
        self.repository = repository
        self.movement_service = movement_service

    async def get_by_id(self, grn_id: uuid.UUID) -> GoodsReceipt:
        grn = await self.repository.get_by_id(grn_id)
        if not grn:
            raise ValidationException(message="Goods Receipt not found")
        return grn

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[GoodsReceipt], int]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, schema: GoodsReceiptCreate, created_by: uuid.UUID) -> GoodsReceipt:
        existing = await self.repository.get_by_grn_number(schema.grn_number)
        if existing:
            raise ValidationException(message=f"GRN number {schema.grn_number} already exists")

        # 1. Create the Goods Receipt document
        grn = GoodsReceipt(
            grn_number=schema.grn_number,
            supplier_id=schema.supplier_id,
            warehouse_id=schema.warehouse_id,
            receipt_date=schema.receipt_date,
            invoice_number=schema.invoice_number,
            challan_number=schema.challan_number,
            remarks=schema.remarks,
            status="POSTED",
            created_by=created_by,
            updated_by=created_by
        )
        
        items = []
        for item_schema in schema.items:
            item = GoodsReceiptItem(
                sku_id=item_schema.sku_id,
                quantity=item_schema.quantity,
                unit_of_measure=item_schema.unit_of_measure,
                created_by=created_by,
                updated_by=created_by
            )
            items.append(item)
            
        grn.items = items
        saved_grn = await self.repository.create(grn)

        # 2. Trigger Inventory Movements for each received item (The Truth Engine)
        today = datetime.now(timezone.utc).date()
        for i, item in enumerate(saved_grn.items):
            movement_request = InventoryMovementCreate(
                movement_number=f"MOV-GRN-{saved_grn.grn_number}-{i+1}",
                movement_type="PURCHASE_RECEIPT",
                movement_date=saved_grn.receipt_date,
                posting_date=today,
                status="POSTED",
                warehouse_id=saved_grn.warehouse_id,
                sku_id=item.sku_id,
                quantity=item.quantity,
                unit_cost=0.0, # Costing is handled by Vyapar
                reference_type="GRN",
                reference_number=saved_grn.grn_number,
                reference_id=saved_grn.supplier_id
            )
            await self.movement_service.create_movement(movement_request, created_by)

        return saved_grn
