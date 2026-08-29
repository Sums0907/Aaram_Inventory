import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult, ProvenanceMetadata
from src.domains.context.handlers.base import BaseCapabilityHandler
from src.domains.inventory.services.job_work import JobWorkService

class JobworkStatusCapabilityHandler(BaseCapabilityHandler):
    def __init__(self, jobwork_service: JobWorkService):
        self.jobwork_service = jobwork_service

    def get_target_parameters(self) -> dict[str, str]:
        return {
            "inventory.entity.job_worker": "UUID",
            "inventory.entity.sku": "UUID",
            "inventory.status.job_work": "STRING"
        }

    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        job_worker_id = None
        sku_id = None
        
        # Parse constraints
        for constraint in request.requirement.semantic_constraints:
            if constraint.identity == "inventory.entity.job_worker" and constraint.operator == "EQUALS":
                if hasattr(constraint, "resolution") and constraint.resolution and constraint.resolution.status == "RESOLVED":
                    job_worker_id = constraint.resolution.resolved_value
                else:
                    try:
                        job_worker_id = uuid.UUID(str(constraint.bound_value))
                    except ValueError:
                        return ContextCapabilityResult(
                            status="ERROR",
                            error_message="Invalid UUID format for inventory.entity.job_worker"
                        )
            elif constraint.identity == "inventory.entity.sku" and constraint.operator == "EQUALS":
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
            elif constraint.identity == "inventory.status.job_work" and constraint.operator == "EQUALS":
                status_filter = str(constraint.bound_value).upper()

        if not job_worker_id:
            return ContextCapabilityResult(
                status="ERROR",
                error_message="Missing required exact constraint for inventory.entity.job_worker."
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
