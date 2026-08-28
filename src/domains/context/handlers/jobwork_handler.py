import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult, ProvenanceMetadata
from src.domains.context.handlers.base import BaseCapabilityHandler
from src.domains.inventory.services.job_work import JobWorkService

class JobworkStatusCapabilityHandler(BaseCapabilityHandler):
    def __init__(self, jobwork_service: JobWorkService):
        self.jobwork_service = jobwork_service

    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        job_worker_id = None
        sku_id = None
        
        # Parse constraints
        for constraint in request.requirement.semantic_constraints:
            if constraint.identity == "inventory.entity.jobwork_vendor" and constraint.operator == "EQUALS":
                try:
                    job_worker_id = uuid.UUID(str(constraint.bound_value))
                except ValueError:
                    return ContextCapabilityResult(
                        status="ERROR",
                        error_message="Invalid UUID format for inventory.entity.jobwork_vendor"
                    )
            elif constraint.identity == "inventory.entity.sku" and constraint.operator == "EQUALS":
                try:
                    sku_id = uuid.UUID(str(constraint.bound_value))
                except ValueError:
                    return ContextCapabilityResult(
                        status="ERROR",
                        error_message="Invalid UUID format for inventory.entity.sku"
                    )

        if not job_worker_id:
            return ContextCapabilityResult(
                status="ERROR",
                error_message="Missing required exact constraint for jobwork_vendor."
            )

        try:
            # Uses the custody ledger function which handles aggregation
            ledger_data = await self.jobwork_service.get_custody_ledger(supplier_id=job_worker_id, item_id=sku_id)
            
            return ContextCapabilityResult(
                status="SUCCESS",
                data={"job_worker_id": str(job_worker_id), "sku_id": str(sku_id) if sku_id else None, "custody_ledger": ledger_data},
                provenance_metadata=ProvenanceMetadata(
                    retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
                    business_timestamp=datetime.now(timezone.utc).isoformat(),
                    derivation_metadata="Calculated via JobWorkService.get_custody_ledger"
                )
            )
            
        except Exception as e:
            return ContextCapabilityResult(
                status="DATA_UNAVAILABLE",
                error_message=f"Failed to retrieve jobwork status: {str(e)}"
            )
