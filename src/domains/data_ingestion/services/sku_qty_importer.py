import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy import select

from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService
from src.domains.data_ingestion.services.master_data_importer import (
    BaseMasterDataImporter, ImportResult, ImportRowResult, ImportAction
)
from decimal import Decimal

class SKUQtyImporter(BaseMasterDataImporter):
    
    def _safe_decimal(self, val: Any) -> Decimal:
        try:
            return Decimal(str(val)) if val else Decimal("0")
        except (ValueError, TypeError, Exception):
            return Decimal("0")

    async def import_data(self, data: List[Dict[str, Any]], is_dry_run: bool = True) -> ImportResult:
        result = ImportResult(entity_type="SKU_QTY_BULK_MAPPING", total_records=len(data))
        
        # 1. Fetch SKUs to match against item_code
        skus_stmt = select(SKUModel)
        skus_list = (await self.session.execute(skus_stmt)).scalars().all()
        skus_by_item_code = {s.item_code: s for s in skus_list}
        
        # 2. Get default warehouse
        warehouse_stmt = select(WarehouseModel).limit(1)
        default_warehouse = (await self.session.execute(warehouse_stmt)).scalars().first()
        if not default_warehouse:
            result.global_errors.append("No warehouse configured in the system. Please create a warehouse before importing stock quantities.")
            # If no warehouse, we must fail everything.
            return result

        warehouse_id = default_warehouse.id
        
        # Setup InventoryMovementService
        from src.domains.inventory.repositories.balance import InventoryBalanceRepository
        from src.domains.inventory.repositories.exception import InventoryExceptionRepository
        from src.domains.inventory.services.confidence_engine import ConfidenceEngine
        
        movement_repo = InventoryMovementRepository(self.session)
        balance_repo = InventoryBalanceRepository(self.session)
        exc_repo = InventoryExceptionRepository(self.session)
        confidence_engine = ConfidenceEngine(exc_repo, movement_repo)
        balance_calculator = BalanceCalculatorService(balance_repo, movement_repo, exc_repo, confidence_engine)
        
        movement_service = InventoryMovementService(movement_repo, balance_calculator)
        
        # We need a system user ID for the movement creator (using a dummy UUID for system imports)
        system_user_id = uuid.UUID("00000000-0000-0000-0000-000000000000")
        
        today = datetime.now(timezone.utc).date()
        
        for idx, row in enumerate(data):
            row_num = idx + 1
            
            sku_id_str = str(row.get("Sku Id", "")).strip()
            quantity_str = row.get("Quantity")
            
            if not sku_id_str:
                result.failed_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.FAILED,
                    errors=["Missing required field 'Sku Id'"]
                ))
                continue
                
            sku = skus_by_item_code.get(sku_id_str)
            if not sku:
                # Missing SKU -> IGNORED per requirements
                result.ignored_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.IGNORED,
                    identifier=sku_id_str,
                    errors=["SKU not found in system"]
                ))
                continue
                
            csv_qty = self._safe_decimal(quantity_str)
            
            # Fetch current balance
            current_balance = await movement_service.get_balance(warehouse_id=warehouse_id, sku_id=sku.id)
            
            difference = csv_qty - current_balance
            
            if difference == 0:
                result.ignored_count += 1
                result.row_results.append(ImportRowResult(
                    row_index=row_num, action=ImportAction.IGNORED,
                    identifier=sku_id_str,
                    errors=["Quantity is already equal to system balance"]
                ))
                continue
                
            # Create Movement if not dry run
            if not is_dry_run:
                movement_schema = InventoryMovementCreate(
                    movement_number=f"ADJ-{uuid.uuid4().hex[:8].upper()}",
                    movement_type="MANUAL_ADJUSTMENT",
                    movement_date=today,
                    posting_date=today,
                    status="POSTED",
                    warehouse_id=warehouse_id,
                    sku_id=sku.id,
                    quantity=float(difference),
                    unit_cost=0.0,
                    reference_type="BULK_IMPORT",
                    reference_number=f"IMP-{today.strftime('%Y%m%d')}",
                    reference_id=uuid.uuid4()
                )
                await movement_service.create_movement(movement_schema, system_user_id, session=self.session)
                
            # Assume success
            result.updated_count += 1
            result.row_results.append(ImportRowResult(
                row_index=row_num, action=ImportAction.UPDATED,
                identifier=sku_id_str
            ))
            
        return result
