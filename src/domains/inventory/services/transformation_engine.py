import uuid
from typing import List, Callable, AsyncContextManager
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.foundation.exceptions.base import ValidationException
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.masters.models.bom import BOMModel, BOMItemModel
from src.domains.inventory.models.job_work import JobWorkerInventoryModel, InventoryTransformationRecord
from src.domains.inventory.schemas.enums import TransformationReason
from src.domains.inventory.repositories.job_work import JobWorkRepository

class TransformationRequest:
    def __init__(self, target_sku_id: uuid.UUID, target_quantity: int, job_worker_id: uuid.UUID, reference_document: str, warehouse_id: uuid.UUID, reason: TransformationReason = TransformationReason.JOB_WORK):
        self.target_sku_id = target_sku_id
        self.target_quantity = target_quantity
        self.job_worker_id = job_worker_id
        self.reference_document = reference_document
        self.warehouse_id = warehouse_id
        self.reason = reason


class InventoryTransformationEngine:
    def __init__(self, movement_service: InventoryMovementService):
        self.movement_service = movement_service

    async def validate_transformation(self, request: TransformationRequest, session: AsyncSession):
        # 1. Fetch BOM for target SKU
        stmt = select(BOMModel).where(BOMModel.target_item_id == request.target_sku_id, BOMModel.status == "ACTIVE")
        result = await session.execute(stmt)
        bom = result.scalars().first()

        if not bom:
            raise ValidationException(
                message=f"No active Bill of Materials found for SKU. Please create a BOM before receiving this item."
            )

        # Fetch BOM Items
        stmt_items = select(BOMItemModel).where(BOMItemModel.bom_id == bom.id)
        items_result = await session.execute(stmt_items)
        bom_items = items_result.scalars().all()

        # 2. Iterate over BOM components to calculate consumption and update Pending Stock
        for bom_item in bom_items:
            # Calculate required raw material using Decimal to prevent precision loss
            required_qty = Decimal(str(bom_item.quantity)) * Decimal(str(request.target_quantity))

            # Check and update Job Worker Pending Stock
            stmt_stock = select(JobWorkerInventoryModel).where(
                JobWorkerInventoryModel.job_worker_id == request.job_worker_id,
                JobWorkerInventoryModel.item_id == bom_item.component_item_id
            )
            stock_result = await session.execute(stmt_stock)
            jw_stock = stock_result.scalars().first()

            if not jw_stock or jw_stock.pending_quantity < required_qty:
                raise ValidationException(
                    message=f"Insufficient pending stock with Job Worker for component {bom_item.component_item_id}. Required: {required_qty}, Available: {jw_stock.pending_quantity if jw_stock else 0}"
                )

    async def execute_transformation(self, request: TransformationRequest, created_by: uuid.UUID, session: AsyncSession):
        # 1. Fetch BOM for target SKU
        stmt = select(BOMModel).where(BOMModel.target_item_id == request.target_sku_id, BOMModel.status == "ACTIVE")
        result = await session.execute(stmt)
        bom = result.scalars().first()

        # Fetch Target SKU to get Destination UOM
        from src.domains.masters.models.sku import SKUModel
        stmt_sku = select(SKUModel).where(SKUModel.id == request.target_sku_id)
        result_sku = await session.execute(stmt_sku)
        target_sku = result_sku.scalars().first()
        destination_uom_id = target_sku.uom_id if target_sku else None

        if not bom:
            raise ValidationException(
                message=f"No active Bill of Materials found for SKU. Please create a BOM before receiving this item."
            )

        # Fetch BOM Items
        stmt_items = select(BOMItemModel).where(BOMItemModel.bom_id == bom.id)
        items_result = await session.execute(stmt_items)
        bom_items = items_result.scalars().all()

        today = datetime.now(timezone.utc).date()

        # 2. Iterate over BOM components to calculate consumption and update Pending Stock
        for bom_item in bom_items:
            # Calculate required raw material using Decimal
            required_qty = Decimal(str(bom_item.quantity)) * Decimal(str(request.target_quantity))

            # Check and update Job Worker Pending Stock
            stmt_stock = select(JobWorkerInventoryModel).where(
                JobWorkerInventoryModel.job_worker_id == request.job_worker_id,
                JobWorkerInventoryModel.item_id == bom_item.component_item_id
            )
            stock_result = await session.execute(stmt_stock)
            jw_stock = stock_result.scalars().first()

            if not jw_stock or jw_stock.pending_quantity < required_qty:
                raise ValidationException(
                    message=f"Insufficient pending stock with Job Worker for component {bom_item.component_item_id}. Required: {required_qty}, Available: {jw_stock.pending_quantity if jw_stock else 0}"
                )

            # Preserve Decimal precision without casting to int!
            jw_stock.consumed_quantity = Decimal(str(jw_stock.consumed_quantity)) + required_qty
            jw_stock.pending_quantity = Decimal(str(jw_stock.pending_quantity)) - required_qty
            
            # 3. Create RAW_MATERIAL_CONSUMPTION movement
            movement_request = InventoryMovementCreate(
                movement_number=f"MOV-CONS-{request.reference_document}-{uuid.uuid4().hex[:6]}",
                movement_type="RAW_MATERIAL_CONSUMPTION",
                movement_date=today,
                posting_date=today,
                status="POSTED",
                warehouse_id=request.warehouse_id,
                sku_id=bom_item.component_item_id,
                quantity=-required_qty,
                unit_cost=0.0,
                reference_type="TRANSFORMATION",
                reference_number=request.reference_document,
                reference_id=request.job_worker_id
            )
            movement = await self.movement_service.create_movement(movement_request, created_by, session=session)
            jw_stock.last_movement_id = movement.id
            
            # 3b. Allocate FIFO consumption against specific Job Work Issues
            repo = JobWorkRepository(session)
            await repo.allocate_consumption(
                request.job_worker_id,
                bom_item.component_item_id,
                required_qty,
                movement.id,
                created_by
            )

            # 4. Create immutable InventoryTransformationRecord
            record = InventoryTransformationRecord(
                source_item_id=bom_item.component_item_id,
                destination_item_id=request.target_sku_id,
                quantity_consumed=required_qty,
                quantity_produced=request.target_quantity,
                source_uom_id=bom_item.uom_id,
                destination_uom_id=destination_uom_id,
                bom_id=bom.id,
                bom_quantity_per_unit=Decimal(str(bom_item.quantity)),
                job_worker_id=request.job_worker_id,
                reference_document=request.reference_document,
                transformation_reason=request.reason
            )
            session.add(record)

