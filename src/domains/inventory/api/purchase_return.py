from fastapi import APIRouter, Depends, Query, status
from uuid import UUID
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse, PaginatedResponse
from src.foundation.authentication.dependencies import get_current_user, CurrentUser, require_permission
from src.app.container import DomainsContainer
from src.domains.inventory.services.purchase_return import PurchaseReturnService
from src.domains.inventory.schemas.purchase_return import PurchaseReturnCreate, PurchaseReturnResponse

router = APIRouter(prefix="/purchase-returns", tags=["Purchase Returns"])

@router.post("", response_model=SuccessResponse[PurchaseReturnResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_return(
    schema: PurchaseReturnCreate,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_RETURN_CREATE")),
    service: PurchaseReturnService = Depends(Provide[DomainsContainer.inventory.purchase_return_service])
):
    user_uuid = UUID(current_user.id)
    result = await service.create(schema, created_by=user_uuid)
    return SuccessResponse(data=PurchaseReturnResponse.model_validate(result, from_attributes=True), message="Purchase Return created and stock updated")

from src.foundation.api.responses import SuccessResponse, PaginatedResponse, PaginationMeta

@router.get("", response_model=PaginatedResponse[PurchaseReturnResponse])
@inject
async def get_returns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_ACTIVITY_VIEW")),
    service: PurchaseReturnService = Depends(Provide[DomainsContainer.inventory.purchase_return_service])
):
    items, total = await service.get_all(skip=skip, limit=limit)
    response_items = [PurchaseReturnResponse.model_validate(item, from_attributes=True) for item in items]
    meta = PaginationMeta(
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1
    )
    return PaginatedResponse(data=response_items, meta=meta)

@router.get("/{return_id}", response_model=SuccessResponse[PurchaseReturnResponse])
@inject
async def get_return(
    return_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_ACTIVITY_VIEW")),
    service: PurchaseReturnService = Depends(Provide[DomainsContainer.inventory.purchase_return_service])
):
    result = await service.get_by_id(return_id)
    return SuccessResponse(data=PurchaseReturnResponse.model_validate(result, from_attributes=True))
