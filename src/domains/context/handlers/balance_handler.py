import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult, ProvenanceMetadata
from src.domains.context.handlers.base import BaseCapabilityHandler
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService

from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.services.confidence_engine import ConfidenceEngine

class BalanceCapabilityHandler(BaseCapabilityHandler):
    def __init__(self, balance_calculator: BalanceCalculatorService, movement_repository: InventoryMovementRepository, confidence_engine: ConfidenceEngine):
        self.balance_calculator = balance_calculator
        self.movement_repository = movement_repository
        self.confidence_engine = confidence_engine

    def get_target_parameters(self) -> dict[str, str]:
        return {
            "inventory.entity.sku": "UUID",
            "inventory.entity.warehouse": "UUID"
        }

    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        sku_id = None
        warehouse_id = None

        # Parse constraints (Engine has already resolved them to UUIDs)
        for constraint in request.requirement.semantic_constraints:
            if constraint.identity == "inventory.entity.sku" and constraint.operator == "EQUALS":
                if hasattr(constraint, "resolution") and constraint.resolution and constraint.resolution.status == "RESOLVED":
                    sku_id = constraint.resolution.resolved_value
                else:
                    try:
                        sku_id = uuid.UUID(str(constraint.bound_value))
                    except ValueError:
                        return ContextCapabilityResult(
                            status="ERROR",
                            error_message="Invalid UUID format for inventory.entity.sku"
                        )
            elif constraint.identity == "inventory.entity.warehouse" and constraint.operator == "EQUALS":
                if hasattr(constraint, "resolution") and constraint.resolution and constraint.resolution.status == "RESOLVED":
                    warehouse_id = constraint.resolution.resolved_value
                else:
                    try:
                        warehouse_id = uuid.UUID(str(constraint.bound_value))
                    except ValueError:
                        return ContextCapabilityResult(
                            status="ERROR",
                            error_message="Invalid UUID format for inventory.entity.warehouse"
                        )

        if not sku_id:
            return ContextCapabilityResult(
                status="ERROR",
                error_message="Missing required exact constraints for sku."
            )

        try:
            if warehouse_id:
                balance_model = await self.balance_calculator.recalculate_balance(
                    warehouse_id=warehouse_id,
                    sku_id=sku_id
                )
                
                data = {
                    "sku_id": str(balance_model.sku_id),
                    "warehouse_id": str(balance_model.warehouse_id),
                    "total_quantity": float(balance_model.total_quantity),
                    "on_hand_quantity": float(balance_model.on_hand_quantity),
                    "allocated_quantity": float(balance_model.allocated_quantity),
                    "in_transit_quantity": float(balance_model.in_transit_quantity),
                    "confidence_score": float(balance_model.confidence_score) if balance_model.confidence_score else 100.0,
                    "last_calculated_at": balance_model.last_calculated_at.isoformat() if balance_model.last_calculated_at else None
                }
                
                provenance = ProvenanceMetadata(
                    retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
                    business_timestamp=balance_model.last_calculated_at.isoformat() if balance_model.last_calculated_at else datetime.now(timezone.utc).isoformat(),
                    derivation_metadata="Calculated via BalanceCalculatorService.recalculate_balance"
                )
            else:
                global_quantity = await self.movement_repository.get_global_balance(sku_id)
                confidence_response = await self.confidence_engine.calculate_confidence(sku_id, None)
                warehouse_balances = await self.movement_repository.get_warehouse_balances(sku_id)
                
                data = {
                    "sku_id": str(sku_id),
                    "warehouse_id": None,
                    "total_quantity": float(global_quantity),
                    "on_hand_quantity": float(global_quantity),
                    "confidence_score": float(confidence_response.confidence_score),
                    "last_calculated_at": None,
                    "warehouse_balances": {k: float(v) for k, v in warehouse_balances.items()}
                }
                
                provenance = ProvenanceMetadata(
                    retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
                    business_timestamp=datetime.now(timezone.utc).isoformat(),
                    derivation_metadata="Calculated via global sum of Inventory Movements"
                )

            return ContextCapabilityResult(
                status="SUCCESS",
                data=data,
                provenance_metadata=provenance
            )
            
        except Exception as e:
            return ContextCapabilityResult(
                status="DATA_UNAVAILABLE",
                error_message=f"Failed to calculate balance: {str(e)}"
            )
