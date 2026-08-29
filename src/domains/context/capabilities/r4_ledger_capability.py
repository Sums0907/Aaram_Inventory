import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.domains.context.capabilities.r4_protocol import IR4Capability
from src.domains.context.dtos.integration_dtos import ConversationalUnderstanding, CandidateEntity
from src.domains.inventory.services.ledger_service import InventoryLedgerService

class R4LedgerCapability(IR4Capability):
    def __init__(self, ledger_service: InventoryLedgerService):
        self.ledger_service = ledger_service

    @property
    def capability_urn(self) -> str:
        return "urn:aarambooks:inventory:capability:ledger"

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
        if not sku_candidates:
            return {}
            
        sku_id = uuid.UUID(sku_candidates[0].business_id)

        # Parse temporal constraints from R-4
        min_date = None
        for entity in understanding.entities:
            if entity.identity == "inventory.temporal.posting_date":
                # Only accept structural ISO formats
                try:
                    min_date = datetime.fromisoformat(str(entity.value).replace("Z", "+00:00")).date()
                except ValueError:
                    # R4DiscoveryService should trap this limitation before calling fetch_evidence
                    pass

        ledger_response = await self.ledger_service.generate_ledger(sku_id=sku_id)
        
        filtered_entries = []
        for entry in ledger_response.entries:
            posting = entry.movement.posting_date
            if min_date and posting < min_date:
                continue
            
            filtered_entries.append({
                "posting_date": posting.isoformat(),
                "movement_type": entry.movement.movement_type,
                "movement_number": entry.movement.movement_number,
                "quantity": float(entry.movement.quantity),
                "running_balance": float(entry.running_balance),
                "reference_type": getattr(entry.movement, "reference_type", None),
                "reference_number": getattr(entry.movement, "reference_number", None)
            })
            
        return {
            "sku_id": str(sku_id),
            "generated_at": ledger_response.generated_at.isoformat(),
            "ledger_entries": filtered_entries
        }
