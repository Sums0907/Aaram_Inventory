from fastapi import APIRouter, Depends, Query, status
from uuid import UUID
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse, PaginatedResponse
from src.foundation.authentication.dependencies import get_current_user, CurrentUser, require_permission
from src.app.container import DomainsContainer
from src.domains.inventory.services.goods_receipt import GoodsReceiptService
from src.domains.inventory.schemas.goods_receipt import GoodsReceiptCreate, GoodsReceiptResponse

router = APIRouter(prefix="/goods-receipts", tags=["Goods Receipts"])

@router.post("", response_model=SuccessResponse[GoodsReceiptResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_grn(
    schema: GoodsReceiptCreate,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_RECEIPT_CREATE")),
    service: GoodsReceiptService = Depends(Provide[DomainsContainer.goods_receipt_service_with_accounting])
):
    user_uuid = UUID(current_user.id)
    result = await service.create(schema, created_by=user_uuid)
    return SuccessResponse(data=GoodsReceiptResponse.model_validate(result, from_attributes=True), message="Goods Receipt created and stock updated")

from src.foundation.api.responses import SuccessResponse, PaginatedResponse, PaginationMeta

@router.get("", response_model=PaginatedResponse[GoodsReceiptResponse])
@inject
async def get_grns(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_ACTIVITY_VIEW")),
    service: GoodsReceiptService = Depends(Provide[DomainsContainer.inventory.goods_receipt_service])
):
    items, total = await service.get_all(skip=skip, limit=limit)
    response_items = [GoodsReceiptResponse.model_validate(item, from_attributes=True) for item in items]
    meta = PaginationMeta(
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1
    )
    return PaginatedResponse(data=response_items, meta=meta)

@router.get("/{grn_id}", response_model=SuccessResponse[GoodsReceiptResponse])
@inject
async def get_grn(
    grn_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_ACTIVITY_VIEW")),
    service: GoodsReceiptService = Depends(Provide[DomainsContainer.inventory.goods_receipt_service])
):
    result = await service.get_by_id(grn_id)
    return SuccessResponse(data=GoodsReceiptResponse.model_validate(result, from_attributes=True))
