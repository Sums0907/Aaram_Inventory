from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from src.foundation.authentication.dependencies import get_current_user, CurrentIdentityContext
from src.domains.context.contracts import ContextCapabilityRequest, ContextCapabilityResult
from src.domains.context.engine import ContextEngine
from src.domains.context.dependency_injection import ContextContainer

router = APIRouter(
    prefix="/context",
    tags=["Context Capability Exposure"]
)

# Capability -> Required Permission mapping for authorization
CAPABILITY_PERMISSIONS = {
    "urn:aarambooks:inventory:capability:balance": "INVENTORY_PRODUCT_VIEW",
    "urn:aarambooks:inventory:capability:ledger": "INVENTORY_ACTIVITY_VIEW",
    "urn:aarambooks:inventory:capability:jobwork_status": "INVENTORY_JOBWORK_VIEW",
    "urn:aarambooks:inventory:capability:exception_status": "INVENTORY_EXCEPTION_VIEW",
}

@router.post("/resolve", response_model=ContextCapabilityResult)
@inject
async def resolve_capability(
    request: ContextCapabilityRequest,
    current_user: CurrentIdentityContext = Depends(get_current_user),
    engine: ContextEngine = Depends(Provide[ContextContainer.context_engine])
):
    """
    Generic capability resolution endpoint implementing the Stage F Brain Protocol.
    """
    # 1. Authorization Check
    urn = request.capability_urn
    required_permission = CAPABILITY_PERMISSIONS.get(urn)
    
    if not required_permission:
        return ContextCapabilityResult(
            status="ERROR",
            error_message=f"Capability URN '{urn}' is not registered in AaramInventory CEM."
        )

    has_admin_role = "AARAM_BOOKS_ADMIN" in current_user.roles or "AARAM_INVENTORY_ADMIN" in current_user.roles
    if required_permission not in current_user.permissions and not has_admin_role:
        return ContextCapabilityResult(
            status="UNAUTHORIZED",
            error_message=f"Missing required physical permission '{required_permission}' for this capability."
        )

    # 2. Blind Dispatch to Engine
    # The ContextEngine performs zero NLP/Semantic logic. It just executes the physical translation.
    try:
        return await engine.resolve(request)
    except Exception as e:
        return ContextCapabilityResult(
            status="ERROR",
            error_message=f"Internal CEM routing fault: {str(e)}"
        )
