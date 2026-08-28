import uuid
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult, ProvenanceMetadata
from src.domains.context.handlers.base import BaseCapabilityHandler
from src.domains.inventory.services.exception import InventoryExceptionService

class ExceptionStatusCapabilityHandler(BaseCapabilityHandler):
    def __init__(self, exception_service: InventoryExceptionService):
        self.exception_service = exception_service

    async def handle(self, request: ContextCapabilityRequest) -> ContextCapabilityResult:
        sku_id = None
        min_date = None
        
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
            elif constraint.identity == "inventory.temporal.exception_date":
                try:
                    parsed_date = datetime.fromisoformat(str(constraint.bound_value).replace("Z", "+00:00")).date()
                    if constraint.operator in ["GREATER_THAN", "GREATER_THAN_EQUALS"]:
                        min_date = parsed_date
                except ValueError:
                    pass

        if not sku_id:
            return ContextCapabilityResult(
                status="ERROR",
                error_message="Missing required exact constraint for sku."
            )

        try:
            exceptions = await self.exception_service.get_open_exceptions_for_sku(sku_id=sku_id)
            
            # Post-filter if temporal constraints provided
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
                
            return ContextCapabilityResult(
                status="SUCCESS",
                data={"sku_id": str(sku_id), "open_exceptions": filtered_exceptions},
                provenance_metadata=ProvenanceMetadata(
                    retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
                    business_timestamp=datetime.now(timezone.utc).isoformat(),
                    derivation_metadata="Retrieved via InventoryExceptionService.get_open_exceptions_for_sku"
                )
            )
            
        except Exception as e:
            return ContextCapabilityResult(
                status="DATA_UNAVAILABLE",
                error_message=f"Failed to retrieve exceptions: {str(e)}"
            )
