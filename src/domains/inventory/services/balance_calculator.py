from uuid import UUID
import uuid
from datetime import datetime, timezone
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.repositories.exception import InventoryExceptionRepository
from src.domains.inventory.models.balance import InventoryBalanceModel
from src.domains.inventory.models.exception import InventoryExceptionModel
from src.domains.inventory.services.confidence_engine import ConfidenceEngine

class BalanceCalculatorService:
    def __init__(
        self, 
        balance_repository: InventoryBalanceRepository, 
        movement_repository: InventoryMovementRepository,
        exception_repository: InventoryExceptionRepository,
        confidence_engine: ConfidenceEngine
    ):
        self.balance_repository = balance_repository
        self.movement_repository = movement_repository
        self.exception_repository = exception_repository
        self.confidence_engine = confidence_engine
        
    async def recalculate_balance(self, warehouse_id: UUID, sku_id: UUID, session=None) -> InventoryBalanceModel:
        """
        Recalculates the projected balance from movements and runs the confidence engine.
        """
        # 1. Recalculate quantity directly from posted movements
        projected_quantity = await self.movement_repository.get_balance(warehouse_id, sku_id, session=session)
        
        # 1b. Catch Negative Inventory
        if projected_quantity < 0:
            exc = InventoryExceptionModel(
                id=uuid.uuid4(),
                exception_number=f"EXC-{sku_id}-NEG-{uuid.uuid4().hex[:8]}",
                sku_id=sku_id,
                warehouse_id=warehouse_id,
                status="OPEN",
                resolution_notes="Negative Inventory detected",
                exception_date=datetime.now(timezone.utc),
                source_system="ENGINE",
                expected_quantity=0,
                actual_quantity=int(projected_quantity),
                difference=int(projected_quantity)
            )
            await self.exception_repository.save(exc, session=session)
        
        # 2. Get Confidence Score
        confidence_response = await self.confidence_engine.calculate_confidence(sku_id, warehouse_id)
        confidence_score = confidence_response.confidence_score
        confidence_reasons = confidence_response.positive_signals + confidence_response.negative_signals
        
        # 3. Update or Create Balance Model
        balance = await self.balance_repository.get_balance(warehouse_id, sku_id, session=session)
        
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
        return await self.balance_repository.save(balance, session=session)
