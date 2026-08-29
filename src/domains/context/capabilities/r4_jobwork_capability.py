import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.domains.context.capabilities.r4_protocol import IR4Capability
from src.domains.context.dtos.integration_dtos import ConversationalUnderstanding, CandidateEntity
from src.domains.inventory.services.job_work import JobWorkService

class R4JobworkCapability(IR4Capability):
    """
    R-4 Business Discovery for Jobwork Status.
    """
    def __init__(self, jobwork_service: JobWorkService):
        self.jobwork_service = jobwork_service
        self._urn = "urn:aarambooks:inventory:capability:jobwork_status"
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
            
        has_job_worker = False
        for entity in understanding.entities:
            if entity.identity == "inventory.entity.job_worker":
                has_job_worker = True
                
        return has_job_worker

    async def fetch_evidence(
        self, 
        understanding: ConversationalUnderstanding, 
        resolved_candidates: Dict[str, List[CandidateEntity]]
    ) -> Dict[str, Any]:
        
        job_worker_candidates = resolved_candidates.get("inventory.entity.job_worker", [])
        if not job_worker_candidates:
            raise ValueError("No resolved candidates for inventory.entity.job_worker")
            
        job_worker_id = uuid.UUID(job_worker_candidates[0].business_id)
        
        sku_id = None
        sku_candidates = resolved_candidates.get("inventory.entity.sku", [])
        if sku_candidates:
            sku_id = uuid.UUID(sku_candidates[0].business_id)
            
        ledger_data = await self.jobwork_service.get_custody_ledger(supplier_id=job_worker_id, item_id=sku_id)
        
        return {
            "job_worker_id": str(job_worker_id),
            "sku_id": str(sku_id) if sku_id else None,
            "custody_ledger": ledger_data
        }
