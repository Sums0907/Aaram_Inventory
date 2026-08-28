import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult, ProvenanceMetadata
from src.domains.context.handlers.base import BaseCapabilityHandler
from src.domains.inventory.services.ledger_service import InventoryLedgerService

class LedgerCapabilityHandler(BaseCapabilityHandler):
    def __init__(self, ledger_service: InventoryLedgerService):
        self.ledger_service = ledger_service

    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        sku_id = None
        min_date = None
        max_date = None
        
        # Parse constraints
        for constraint in request.requirement.semantic_constraints:
            if constraint.identity == "inventory.entity.sku" and constraint.operator == "EQUALS":
                try:
                    sku_id = uuid.UUID(str(constraint.bound_value))
                except ValueError:
                    return ContextCapabilityResult(
                        status="ERROR",
                        error_message="Invalid UUID format for inventory.entity.sku"
                    )
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
