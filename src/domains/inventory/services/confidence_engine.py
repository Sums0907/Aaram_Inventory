from uuid import UUID
from typing import Optional
from src.domains.inventory.repositories.exception import InventoryExceptionRepository
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.schemas.enums import ExceptionSource
from src.domains.inventory.schemas.confidence import InventoryConfidenceResponse

class ConfidenceEngine:
    def __init__(self, exception_repository: InventoryExceptionRepository, movement_repository: InventoryMovementRepository):
        self.exception_repository = exception_repository
        self.movement_repository = movement_repository
        
    async def calculate_confidence(self, sku_id: UUID, warehouse_id: Optional[UUID] = None) -> InventoryConfidenceResponse:
        """
        Determines the inventory confidence score based on open exceptions and movement verification.
        Evaluates at the SKU level, optionally filtered by warehouse.
        """
        score = 100
        positive_signals = []
        negative_signals = []
        
        # 1. Check open exceptions
        open_exceptions = await self.exception_repository.get_open_exceptions_for_sku(sku_id)
        
        has_marketplace_exception = False
        has_accounting_exception = False
        has_physical_exception = False
        
        for exc in open_exceptions:
            if warehouse_id and exc.warehouse_id != warehouse_id:
                continue
                
            if exc.source_system == ExceptionSource.MARKETPLACE:
                has_marketplace_exception = True
            elif exc.source_system == ExceptionSource.ACCOUNTING:
                has_accounting_exception = True
            elif exc.source_system == ExceptionSource.PHYSICAL:
                has_physical_exception = True
                
        if has_marketplace_exception:
            score -= 10
            negative_signals.append("Marketplace discrepancy exists.")
        else:
            positive_signals.append("Marketplace synchronized.")
            
        if has_accounting_exception:
            score -= 15
            negative_signals.append("Accounting discrepancy exists.")
        else:
            positive_signals.append("Accounting reconciled.")
            
        if has_physical_exception:
            score -= 20
            negative_signals.append("Open physical stock exception.")
        else:
            positive_signals.append("No open physical discrepancies.")
            
        # 2. Check for negative inventory
        # If the sku has no warehouse filter, we would normally sum all warehouses,
        # but here we can just sum all movements for the SKU.
        movements = await self.movement_repository.get_movements_for_sku(sku_id)
        total_qty = 0
        for mov in movements:
            if not warehouse_id or mov.warehouse_id == warehouse_id:
                total_qty += mov.quantity
                
        if total_qty < 0:
            score -= 30
            negative_signals.append("Negative inventory balance detected.")
        else:
            positive_signals.append("Stock balance is mathematically viable (>= 0).")
            
        # 3. Check for manual adjustments (hypothetical, as they reduce confidence)
        has_manual_adj = any(mov.movement_type == "ADJUSTMENT" for mov in movements if not warehouse_id or mov.warehouse_id == warehouse_id)
        if has_manual_adj:
            score -= 5
            negative_signals.append("Manual adjustments bypass normal operational flow.")
        else:
            positive_signals.append("No manual adjustments. Fully event-driven history.")
            
        # Keep score between 0 and 100
        score = max(0, min(100, score))
        
        return InventoryConfidenceResponse(
            sku_id=sku_id,
            confidence_score=score,
            positive_signals=positive_signals,
            negative_signals=negative_signals
        )
