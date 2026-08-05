from uuid import UUID
from datetime import datetime, timezone
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.models.balance import InventoryBalanceModel
from src.domains.inventory.services.confidence_engine import ConfidenceEngine

class BalanceCalculatorService:
    def __init__(
        self, 
        balance_repository: InventoryBalanceRepository, 
        movement_repository: InventoryMovementRepository,
        confidence_engine: ConfidenceEngine
    ):
        self.balance_repository = balance_repository
        self.movement_repository = movement_repository
        self.confidence_engine = confidence_engine
        
    async def recalculate_balance(self, warehouse_id: UUID, sku_id: UUID) -> InventoryBalanceModel:
        """
        Recalculates the projected balance from movements and runs the confidence engine.
        """
        # 1. Recalculate quantity directly from posted movements
        projected_quantity = await self.movement_repository.get_balance(warehouse_id, sku_id)
        
        # 2. Get Confidence Score
        confidence_score, confidence_reasons = await self.confidence_engine.calculate_confidence(warehouse_id, sku_id)
        
        # 3. Update or Create Balance Model
        balance = await self.balance_repository.get_balance(warehouse_id, sku_id)
        
        if not balance:
            balance = InventoryBalanceModel(
                warehouse_id=warehouse_id,
                sku_id=sku_id,
                quantity_on_hand=projected_quantity,
                confidence_score=confidence_score,
                confidence_reasons=confidence_reasons,
                last_movement_date=datetime.now(timezone.utc)
            )
        else:
            balance.quantity_on_hand = projected_quantity
            balance.confidence_score = confidence_score
            balance.confidence_reasons = confidence_reasons
            balance.last_movement_date = datetime.now(timezone.utc)
            
        # 4. Save to DB
        return await self.balance_repository.save(balance)
