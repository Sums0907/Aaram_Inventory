import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult, ProvenanceMetadata
from src.domains.context.handlers.base import BaseCapabilityHandler
from src.domains.inventory.services.ledger_service import InventoryLedgerService

class LedgerCapabilityHandler(BaseCapabilityHandler):
    def __init__(self, ledger_service: InventoryLedgerService):
        self.ledger_service = ledger_service

    def get_target_parameters(self) -> dict[str, str]:
        return {
            "inventory.entity.sku": "UUID",
            "inventory.entity.warehouse": "UUID",
            "inventory.temporal.month": "STRING"
        }

    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        sku_id = None
        warehouse_id = None
        month_str = None
        min_date = None
        max_date = None
        
        # Parse constraints
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
            elif constraint.identity == "inventory.temporal.month" and constraint.operator == "EQUALS":
                month_str = str(constraint.bound_value)
            elif constraint.identity == "inventory.temporal.posting_date":
                try:
                    parsed_date = datetime.fromisoformat(str(constraint.bound_value).replace("Z", "+00:00")).date()
                    if constraint.operator in ["GREATER_THAN", "GREATER_THAN_EQUALS"]:
                        min_date = parsed_date
                    elif constraint.operator in ["LESS_THAN", "LESS_THAN_EQUALS"]:
                        max_date = parsed_date
                except ValueError:
                    pass

        if not sku_id:
            return ContextCapabilityResult(
                status="ERROR",
                error_message="Missing required exact constraint for sku."
            )

        try:
            ledger_response = await self.ledger_service.generate_ledger(sku_id=sku_id)
            
            # Post-filter if temporal constraints provided
            filtered_entries = []
            for entry in ledger_response.entries:
                posting = entry.movement.posting_date
                if min_date and posting < min_date:
                    continue
                if max_date and posting > max_date:
                    continue
                
                filtered_entries.append({
                    "movement_number": entry.movement.movement_number,
                    "movement_type": entry.movement.movement_type,
                    "quantity": float(entry.movement.quantity),
                    "posting_date": posting.isoformat(),
                    "running_balance": float(entry.running_balance)
                })
                
            return ContextCapabilityResult(
                status="SUCCESS",
                data={"sku_id": str(sku_id), "entries": filtered_entries},
                provenance_metadata=ProvenanceMetadata(
                    retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
                    business_timestamp=datetime.now(timezone.utc).isoformat(),
                    derivation_metadata="Calculated via InventoryLedgerService.generate_ledger"
                )
            )
            
        except Exception as e:
            return ContextCapabilityResult(
                status="DATA_UNAVAILABLE",
                error_message=f"Failed to generate ledger: {str(e)}"
            )
