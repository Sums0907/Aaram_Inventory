from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
import uuid

from src.foundation.api.responses import SuccessResponse
from src.foundation.authentication.dependencies import require_permission, CurrentUser
from src.domains.inventory.services.exception import InventoryExceptionService
from src.domains.inventory.schemas.exception import (
    ExceptionListResponse,
    ResolveExceptionRequest,
    InventoryExceptionResponse
)
from src.app.container import DomainsContainer

router = APIRouter(prefix="/inventory/exceptions", tags=["inventory-exceptions"])

@router.get("", response_model=SuccessResponse[ExceptionListResponse])
@inject
async def get_exceptions(
    limit: int = 50,
    exception_service: InventoryExceptionService = Depends(Provide[DomainsContainer.inventory.exception_service]),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_EXCEPTION_VIEW"))
):
    exceptions = await exception_service.get_all_open_exceptions(limit=limit)
    response_data = ExceptionListResponse(
        total_count=len(exceptions),
        items=exceptions
    )
    return SuccessResponse(data=response_data)

@router.post("/{exception_id}/resolve", response_model=SuccessResponse[InventoryExceptionResponse])
@inject
async def resolve_exception(
    exception_id: uuid.UUID,
    request: ResolveExceptionRequest,
    exception_service: InventoryExceptionService = Depends(Provide[DomainsContainer.inventory.exception_service]),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_EXCEPTION_RESOLVE"))
):
    resolved = await exception_service.resolve_exception(
        exception_id=exception_id, 
        resolution_notes=request.resolution_notes
    )
    return SuccessResponse(data=resolved)
