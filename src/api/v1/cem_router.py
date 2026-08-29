from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from src.foundation.authentication.dependencies import get_current_user, CurrentIdentityContext
from src.domains.context.dtos.integration_dtos import AbstractEvidenceRequest, BusinessEvidenceResponse, BusinessRealityStatus
from src.domains.context.services.r4_discovery_service import R4DiscoveryService
from src.domains.context.services.r7_execution_service import R7ExecutionService
from src.domains.context.dependency_injection import ContextContainer

router = APIRouter(
    prefix="/cem/v1",
    tags=["Context Execution Module R-4"]
)

@router.post("/discover", response_model=BusinessEvidenceResponse)
@inject
async def discover_business_reality(
    request: AbstractEvidenceRequest,
    current_user: CurrentIdentityContext = Depends(get_current_user),
    discovery_service: R4DiscoveryService = Depends(Provide[ContextContainer.r4_discovery_service])
):
    """
    R-4 Business Discovery Endpoint.
    Receives purely semantic request (without routing IDs).
    Authenticates/authorizes out-of-band via headers.
    """
    # Out-of-band Authorization
    # The application_id/user identity is provided by AaramIdentity in `current_user`.
    # R-4 MAY enforce local business authorization here.
    has_admin_role = "AARAM_BOOKS_ADMIN" in current_user.roles or "AARAM_INVENTORY_ADMIN" in current_user.roles
    if not has_admin_role and not current_user.permissions:
        return BusinessEvidenceResponse(
            status=BusinessRealityStatus.CAPABILITY_UNAVAILABLE,
            execution_limitations=[{"missing_parameter": "Authorization", "reason": "Missing required physical permissions."}]
        )

    # Orchestrate R-4 Discovery
    try:
        return await discovery_service.discover(request)
    except Exception as e:
        return BusinessEvidenceResponse(
            status=BusinessRealityStatus.EVIDENCE_UNAVAILABLE,
            execution_limitations=[{"missing_parameter": "Internal", "reason": str(e)}]
        )

@router.post("/execute", response_model=BusinessEvidenceResponse)
@inject
async def execute_business_reality(
    request: AbstractEvidenceRequest,
    current_user: CurrentIdentityContext = Depends(get_current_user),
    execution_service: R7ExecutionService = Depends(Provide[ContextContainer.r7_execution_service])
):
    """
    R-7 Business Execution Endpoint.
    Receives purely semantic request mapped to ACTION intent.
    Executes actual mutations through R-7 capabilities.
    """
    has_admin_role = "AARAM_BOOKS_ADMIN" in current_user.roles or "AARAM_INVENTORY_ADMIN" in current_user.roles
    if not has_admin_role and not current_user.permissions:
        return BusinessEvidenceResponse(
            status=BusinessRealityStatus.CAPABILITY_UNAVAILABLE,
            execution_limitations=[{"missing_parameter": "Authorization", "reason": "Missing required physical permissions."}]
        )

    if request.classified_requirement.understanding.intent != "ACTION":
        return BusinessEvidenceResponse(
            status=BusinessRealityStatus.CAPABILITY_UNAVAILABLE,
            execution_limitations=[{"missing_parameter": "Intent", "reason": "/execute strictly requires ACTION intent."}]
        )

    execution_context = {
        "user_id": current_user.user_id,
        "application_id": current_user.application_id
    }

    try:
        return await execution_service.execute(request, execution_context)
    except Exception as e:
        return BusinessEvidenceResponse(
            status=BusinessRealityStatus.EVIDENCE_UNAVAILABLE,
            execution_limitations=[{"missing_parameter": "Internal", "reason": str(e)}]
        )
