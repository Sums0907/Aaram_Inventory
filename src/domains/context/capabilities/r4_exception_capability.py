import uuid
from typing import Dict, Any, List
from datetime import datetime
from src.domains.context.capabilities.r4_protocol import IR4Capability
from src.domains.context.dtos.integration_dtos import ConversationalUnderstanding, CandidateEntity
from src.domains.inventory.services.exception import InventoryExceptionService

class R4ExceptionCapability(IR4Capability):
    """
    R-4 Business Discovery for Exception Status.
    """
    def __init__(self, exception_service: InventoryExceptionService):
        self.exception_service = exception_service
        self._urn = "urn:aarambooks:inventory:capability:exception_status"
        self._intent = "RETRIEVE"

    @property
    def capability_urn(self) -> str:
        return self._urn

    @property
    def supported_intent(self) -> str:
        return self._intent

    def is_applicable(self, understanding: ConversationalUnderstanding) -> bool:
        if understanding.intent != self._intent:
            return False
            
        has_sku = False
        for entity in understanding.entities:
            if entity.identity == "inventory.entity.sku":
                has_sku = True
                
        return has_sku

    async def fetch_evidence(
        self, 
        understanding: ConversationalUnderstanding, 
        resolved_candidates: Dict[str, List[CandidateEntity]]
    ) -> Dict[str, Any]:
        
        sku_candidates = resolved_candidates.get("inventory.entity.sku", [])
        if not sku_candidates:
            raise ValueError("No resolved candidates for inventory.entity.sku")
            
        sku_id = uuid.UUID(sku_candidates[0].business_id)
        
        min_date = None
        for entity in understanding.entities:
            if entity.identity == "inventory.temporal.exception_date":
                try:
                    parsed_date = datetime.fromisoformat(str(entity.value).replace("Z", "+00:00")).date()
                    if entity.operator in ["GREATER_THAN", "GREATER_THAN_EQUALS"]:
                        min_date = parsed_date
                except ValueError:
                    pass
        
        exceptions = await self.exception_service.repository.get_open_exceptions_for_sku(sku_id=sku_id)
        
        filtered_exceptions = []
        for exc in exceptions:
            if min_date and exc.exception_date < min_date:
                continue
            
            filtered_exceptions.append({
                "exception_number": exc.exception_number,
                "exception_date": exc.exception_date.isoformat(),
                "source_system": exc.source_system,
                "expected_quantity": float(exc.expected_quantity),
                "actual_quantity": float(exc.actual_quantity),
                "difference": float(exc.difference),
                "status": exc.status
            })
            
        return {
            "sku_id": str(sku_id),
            "open_exceptions": filtered_exceptions
        }
