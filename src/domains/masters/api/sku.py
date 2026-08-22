from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser, require_permission
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.sku import SKUCreate, SKUUpdate, SKUResponse
from src.domains.masters.services.sku import SKUService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/skus", tags=["SKU"])

@router.get("", response_model=SuccessResponse[List[SKUResponse]])
@inject
async def list_skus(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_CATALOG_VIEW")),
    service: SKUService = Depends(Provide[MastersContainer.sku_service])
):
    skus = await service.list_skus(skip=skip, limit=limit)
    response_data = [SKUResponse.model_validate(sku, from_attributes=True) for sku in skus]
    return SuccessResponse(data=response_data)

@router.get("/{sku_id}", response_model=SuccessResponse[SKUResponse])
@inject
async def get_sku(
    sku_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_CATALOG_VIEW")),
    service: SKUService = Depends(Provide[MastersContainer.sku_service])
):
    sku = await service.get_sku(sku_id)
    return SuccessResponse(data=SKUResponse.model_validate(sku, from_attributes=True))

@router.post("", response_model=SuccessResponse[SKUResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_sku(
    schema: SKUCreate,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_CREATE")),
    service: SKUService = Depends(Provide[MastersContainer.sku_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    sku = await service.create_sku(schema, created_by=user_uuid)
    return SuccessResponse(data=SKUResponse.model_validate(sku, from_attributes=True))

@router.put("/{sku_id}", response_model=SuccessResponse[SKUResponse])
@inject
async def update_sku(
    sku_id: UUID,
    schema: SKUUpdate,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: SKUService = Depends(Provide[MastersContainer.sku_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    sku = await service.update_sku(sku_id, schema, updated_by=user_uuid)
    return SuccessResponse(data=SKUResponse.model_validate(sku, from_attributes=True))

@router.patch("/{sku_id}/activate", response_model=SuccessResponse[SKUResponse])
@inject
async def activate_sku(
    sku_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: SKUService = Depends(Provide[MastersContainer.sku_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    sku = await service.activate_sku(sku_id, updated_by=user_uuid)
    return SuccessResponse(data=SKUResponse.model_validate(sku, from_attributes=True))

@router.patch("/{sku_id}/deactivate", response_model=SuccessResponse[SKUResponse])
@inject
async def deactivate_sku(
    sku_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: SKUService = Depends(Provide[MastersContainer.sku_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    sku = await service.deactivate_sku(sku_id, updated_by=user_uuid)
    return SuccessResponse(data=SKUResponse.model_validate(sku, from_attributes=True))

@router.patch("/{sku_id}/archive", response_model=SuccessResponse[SKUResponse])
@inject
async def archive_sku(
    sku_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: SKUService = Depends(Provide[MastersContainer.sku_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    sku = await service.archive_sku(sku_id, updated_by=user_uuid)
    return SuccessResponse(data=SKUResponse.model_validate(sku, from_attributes=True))

@router.delete("/{sku_id}", response_model=SuccessResponse[dict])
@inject
async def delete_sku(
    sku_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: SKUService = Depends(Provide[MastersContainer.sku_service])
):
    await service.delete_sku(sku_id)
    return SuccessResponse(data={"message": "SKU deleted successfully"})
