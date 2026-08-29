import uuid
from typing import Dict, Any, List
from src.domains.context.capabilities.r4_protocol import IR4Capability
from src.domains.context.dtos.integration_dtos import ConversationalUnderstanding, CandidateEntity
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.services.confidence_engine import ConfidenceEngine

class R4BalanceCapability(IR4Capability):
    def __init__(
        self,
        balance_calculator: BalanceCalculatorService,
        balance_repository: InventoryBalanceRepository,
        confidence_engine: ConfidenceEngine,
        movement_repository: InventoryMovementRepository
    ):
        self.balance_calculator = balance_calculator
        self.balance_repository = balance_repository
        self.confidence_engine = confidence_engine
        self.movement_repository = movement_repository

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:balance"

    @property
    def supported_intent(self) -> str:
        return "RETRIEVE"

    def get_required_semantics(self) -> List[str]:
        return ["inventory.entity.sku"]

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self.supported_intent:
            return False
            
        has_sku = any(c.identity == "inventory.entity.sku" and c.operator == "EQUALS" for c in understanding.entities)
        
        return has_sku

    async def fetch_evidence(
        self, 
        understanding: ConversationalUnderstanding, 
        resolved_candidates: Dict[str, List[CandidateEntity]]
    ) -> Dict[str, Any]:
        sku_candidates = resolved_candidates.get("inventory.entity.sku", [])
        warehouse_candidates = resolved_candidates.get("inventory.entity.warehouse", [])
        
        if not sku_candidates:
            return {}
            
        sku_id = uuid.UUID(sku_candidates[0].business_id)
        
        warehouse_id = None
        if warehouse_candidates:
            warehouse_id = uuid.UUID(warehouse_candidates[0].business_id)

        if warehouse_id:
            # Legacy behavior from R4DiscoveryService
            balance_model = await self.balance_repository.get_balance(warehouse_id, sku_id)
            
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
                # Fallback to movement repository for a read-only sum for a specific warehouse
                projected_quantity = await self.movement_repository.get_balance(warehouse_id, sku_id)
                confidence_response = await self.confidence_engine.calculate_confidence(sku_id, warehouse_id)
                
                return {
                    "sku_id": str(sku_id),
                    "warehouse_id": str(warehouse_id),
                    "total_quantity": float(projected_quantity),
                    "on_hand_quantity": float(projected_quantity),
                    "confidence_score": float(confidence_response.confidence_score),
                    "last_calculated_at": None
                }
        else:
            # Global balance when warehouse is omitted
            global_quantity = await self.movement_repository.get_global_balance(sku_id)
            confidence_response = await self.confidence_engine.calculate_confidence(sku_id, None)
            warehouse_balances = await self.movement_repository.get_warehouse_balances(sku_id)
            
            return {
                "sku_id": str(sku_id),
                "warehouse_id": None,
                "total_quantity": float(global_quantity),
                "on_hand_quantity": float(global_quantity),
                "confidence_score": float(confidence_response.confidence_score),
                "last_calculated_at": None,
                "warehouse_balances": {k: float(v) for k, v in warehouse_balances.items()}
            }
