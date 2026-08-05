from uuid import UUID
from typing import Tuple, List
from src.domains.inventory.repositories.exception import InventoryExceptionRepository
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.schemas.enums import ExceptionSource

class ConfidenceEngine:
    def __init__(self, exception_repository: InventoryExceptionRepository, movement_repository: InventoryMovementRepository):
        self.exception_repository = exception_repository
        self.movement_repository = movement_repository
        
    async def calculate_confidence(self, warehouse_id: UUID, sku_id: UUID) -> Tuple[int, List[str]]:
        """
        Determines the inventory confidence score based on open exceptions and movement verification.
        Returns: (score (0-100), list of reasons)
        """
        score = 100
        reasons = []
        
        # 1. Check open exceptions
        open_exceptions = await self.exception_repository.get_open_exceptions_for_sku(sku_id)
        
        has_marketplace_exception = False
        has_accounting_exception = False
        has_physical_exception = False
        
        for exc in open_exceptions:
            if exc.warehouse_id != warehouse_id:
                continue
                
            if exc.source_system == ExceptionSource.MARKETPLACE:
                has_marketplace_exception = True
            elif exc.source_system == ExceptionSource.ACCOUNTING:
                has_accounting_exception = True
            elif exc.source_system == ExceptionSource.PHYSICAL:
                has_physical_exception = True
                
        if has_marketplace_exception:
            score -= 10
            reasons.append("⚠ Marketplace discrepancy exists.")
        else:
            reasons.append("✓ Marketplace synchronized.")
            
        if has_accounting_exception:
            score -= 15
            reasons.append("⚠ Accounting discrepancy exists.")
        else:
            reasons.append("✓ Accounting reconciled.")
            
        if has_physical_exception:
            score -= 20
            reasons.append("⚠ Open physical stock exception.")
            
        # 2. Look for recent movements
        # In a real implementation, we might check if the last physical count was > 90 days ago.
        
        # Keep score between 0 and 100
        score = max(0, min(100, score))
        
        return score, reasons
