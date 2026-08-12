import uuid
import logging
from typing import List, Tuple, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.inventory.repositories.goods_receipt import GoodsReceiptRepository
from src.domains.inventory.models.goods_receipt import GoodsReceipt, GoodsReceiptItem
from src.domains.inventory.schemas.goods_receipt import GoodsReceiptCreate
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.foundation.exceptions.base import ValidationException
from src.domains.inventory.schemas.enums import GoodsReceiptType, TransformationReason
from src.domains.inventory.services.transformation_engine import InventoryTransformationEngine, TransformationRequest

log = logging.getLogger(__name__)

class GoodsReceiptService:
    def __init__(
        self,
        repository: GoodsReceiptRepository,
        movement_service: InventoryMovementService,
        transformation_engine: InventoryTransformationEngine,
        expense_service=None,  # Optional: accounting.job_worker.services.expense_service.ExpenseService
    ):
        self.repository = repository
        self.movement_service = movement_service
        self.transformation_engine = transformation_engine
        self.expense_service = expense_service  # Injected only if accounting module is wired

    async def get_by_id(self, grn_id: uuid.UUID) -> GoodsReceipt:
        grn = await self.repository.get_by_id(grn_id)
        if not grn:
            raise ValidationException(message="Goods Receipt not found")
        return grn

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[GoodsReceipt], int]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, schema: GoodsReceiptCreate, created_by: uuid.UUID) -> GoodsReceipt:
        # Establish the transaction boundary for this Goods Receipt
        session = self.repository.session
        
        try:
            existing = await self.repository.get_by_grn_number(schema.grn_number)
            if existing:
                raise ValidationException(message=f"GRN number {schema.grn_number} already exists")

            # 0. Pre-validate transformations to avoid partial commits on error
            if schema.receipt_type == GoodsReceiptType.JOB_WORK_RECEIPT:
                for item_schema in schema.items:
                    engine_request = TransformationRequest(
                        target_sku_id=item_schema.sku_id,
                        target_quantity=item_schema.quantity,
                        job_worker_id=schema.supplier_id,
                        reference_document=schema.grn_number,
                        warehouse_id=schema.warehouse_id,
                        reason=TransformationReason.JOB_WORK
                    )
                    await self.transformation_engine.validate_transformation(engine_request, session=session)

            # 1. Create the Goods Receipt document
            grn = GoodsReceipt(
                grn_number=schema.grn_number,
                supplier_id=schema.supplier_id,
                warehouse_id=schema.warehouse_id,
                receipt_date=schema.receipt_date,
                invoice_number=schema.invoice_number,
                challan_number=schema.challan_number,
                remarks=schema.remarks,
                receipt_type=schema.receipt_type,
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
            
            # Use shared session to save without committing
            saved_grn = await self.repository.create(grn, session=session)

            # 2. Trigger Inventory Movements for each received item (The Truth Engine)
            today = datetime.now(timezone.utc).date()
            for i, item in enumerate(saved_grn.items):
                # Define movement type based on receipt type
                mov_type = "PURCHASE_RECEIPT"
                if saved_grn.receipt_type == GoodsReceiptType.JOB_WORK_RECEIPT:
                    mov_type = "JOB_WORK_RECEIPT"

                movement_request = InventoryMovementCreate(
                    movement_number=f"MOV-GRN-{saved_grn.grn_number}-{i+1}",
                    movement_type=mov_type,
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
                await self.movement_service.create_movement(movement_request, created_by, session=session)

                # 3. If it is a Job Work Receipt, trigger the Transformation Engine
                if saved_grn.receipt_type == GoodsReceiptType.JOB_WORK_RECEIPT:
                    engine_request = TransformationRequest(
                        target_sku_id=item.sku_id,
                        target_quantity=item.quantity,
                        job_worker_id=saved_grn.supplier_id,
                        reference_document=saved_grn.grn_number,
                        warehouse_id=saved_grn.warehouse_id,
                        reason=TransformationReason.JOB_WORK
                    )
                    await self.transformation_engine.execute_transformation(engine_request, created_by, session=session)

                    # 4. Trigger Job Worker Accounting expense (same transaction)
                    if self.expense_service is not None:
                        try:
                            expense = await self.expense_service.create_from_receipt(
                                job_worker_id=saved_grn.supplier_id,
                                sku_id=item.sku_id,
                                quantity=float(item.quantity),
                                receipt_id=saved_grn.id,
                                receipt_number=saved_grn.grn_number,
                                receipt_date=saved_grn.receipt_date,
                                created_by=created_by,
                            )
                            if expense is None:
                                log.warning(
                                    "No Job Work Rate configured for job_worker=%s sku=%s on %s. "
                                    "GRN will proceed without an expense record.",
                                    saved_grn.supplier_id, item.sku_id, saved_grn.receipt_date,
                                )
                        except ValidationException:
                            raise  # Duplicate-expense guard — surface this clearly
                        except Exception as exc:
                            log.error("Expense creation failed for GRN %s: %s", saved_grn.grn_number, exc)
                            raise  # Roll back the entire transaction

            # Commit the entire transaction only if everything succeeds
            await session.commit()
            
            # Refresh to ensure relationships like items are loaded
            await session.refresh(saved_grn)
            # Need to selectinload items, easiest is to get_by_id
            return await self.get_by_id(saved_grn.id)

        except Exception as e:
            # If any failure occurs, rollback the entire transaction block
            await session.rollback()
            raise e

