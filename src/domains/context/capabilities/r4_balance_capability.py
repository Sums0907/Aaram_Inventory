import uuid
from typing import Dict, Any, List
from src.domains.context.capabilities.r4_protocol import IR4Capability
from src.domains.context.dtos.integration_dtos import ConversationalUnderstanding, CandidateEntity
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.services.confidence_engine import ConfidenceEngine

class R4BalanceCapability(IR4Capability):
    def __init__(
        self,
        balance_calculator: BalanceCalculatorService,
        balance_repository: InventoryBalanceRepository,
        confidence_engine: ConfidenceEngine
    ):
        self.balance_calculator = balance_calculator
        self.balance_repository = balance_repository
        self.confidence_engine = confidence_engine

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:balance"

    @property
    def supported_intent(self) -> str:
        return "RETRIEVE"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.sku", "inventory.entity.warehouse"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
            
        has_sku = any(c.identity == "inventory.entity.sku" and c.operator == "EQUALS" for c in understanding.entities)
        has_warehouse = any(c.identity == "inventory.entity.warehouse" and c.operator == "EQUALS" for c in understanding.entities)
        
        return has_sku and has_warehouse

    async def fetch_evidence(
        self, 
        understanding: ConversationalUnderstanding, 
        resolved_candidates: Dict[str, List[CandidateEntity]]
    ) -> Dict[str, Any]:
        sku_candidates = resolved_candidates.get("inventory.entity.sku", [])
        warehouse_candidates = resolved_candidates.get("inventory.entity.warehouse", [])
        
        if not sku_candidates or not warehouse_candidates:
            return {}
            
        sku_id = uuid.UUID(sku_candidates[0].business_id)
        warehouse_id = uuid.UUID(warehouse_candidates[0].business_id)

        # Legacy behavior from R4DiscoveryService
        balance_model = await self.balance_repository.get_balance(uuid.UUID(str(warehouse_id)), uuid.UUID(str(sku_id)))
        
        if balance_model:
            return {
                "sku_id": str(balance_model.sku_id),
                "warehouse_id": str(balance_model.warehouse_id),
                "total_quantity": float(balance_model.quantity_on_hand),
                "on_hand_quantity": float(balance_model.quantity_on_hand),
                "confidence_score": float(balance_model.confidence_score) if balance_model.confidence_score else 100.0,
                "last_calculated_at": balance_model.last_movement_date.isoformat() if balance_model.last_movement_date else None
            }
        else:
            # Fallback to movement repository for a read-only sum
            projected_quantity = 0.0
            confidence_response = await self.confidence_engine.calculate_confidence(uuid.UUID(str(sku_id)), uuid.UUID(str(warehouse_id)))
            
            return {
                "sku_id": str(sku_id),
                "warehouse_id": str(warehouse_id),
                "total_quantity": float(projected_quantity),
                "on_hand_quantity": float(projected_quantity),
                "confidence_score": float(confidence_response.confidence_score),
                "last_calculated_at": None
            }
