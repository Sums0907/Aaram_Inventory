from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.inventory_item import InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse
from src.domains.masters.services.inventory_item import InventoryItemService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/inventory-items", tags=["Inventory Item"])

@router.get("", response_model=SuccessResponse[List[InventoryItemResponse]])
@inject
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(get_current_user),
    service: InventoryItemService = Depends(Provide[MastersContainer.inventory_item_service])
):
    items = await service.list_items(skip=skip, limit=limit)
    
    # Map product_attributes to product_attribute_ids for the response schema
    response_data = []
    for item in items:
        resp_model = InventoryItemResponse.model_validate(item, from_attributes=True)
        resp_model.product_attribute_ids = [attr.id for attr in item.product_attributes]
        response_data.append(resp_model)
        
    return SuccessResponse(data=response_data)

@router.get("/{item_id}", response_model=SuccessResponse[InventoryItemResponse])
@inject
async def get_item(
    item_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: InventoryItemService = Depends(Provide[MastersContainer.inventory_item_service])
):
    item = await service.get_item(item_id)
    resp_model = InventoryItemResponse.model_validate(item, from_attributes=True)
    resp_model.product_attribute_ids = [attr.id for attr in item.product_attributes]
    return SuccessResponse(data=resp_model)

@router.post("", response_model=SuccessResponse[InventoryItemResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_item(
    schema: InventoryItemCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: InventoryItemService = Depends(Provide[MastersContainer.inventory_item_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    item = await service.create_item(schema, created_by=user_uuid)
    resp_model = InventoryItemResponse.model_validate(item, from_attributes=True)
    resp_model.product_attribute_ids = [attr.id for attr in item.product_attributes]
    return SuccessResponse(data=resp_model)

@router.put("/{item_id}", response_model=SuccessResponse[InventoryItemResponse])
@inject
async def update_item(
    item_id: UUID,
    schema: InventoryItemUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: InventoryItemService = Depends(Provide[MastersContainer.inventory_item_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    item = await service.update_item(item_id, schema, updated_by=user_uuid)
    resp_model = InventoryItemResponse.model_validate(item, from_attributes=True)
    resp_model.product_attribute_ids = [attr.id for attr in item.product_attributes]
    return SuccessResponse(data=resp_model)

@router.patch("/{item_id}/activate", response_model=SuccessResponse[InventoryItemResponse])
@inject
async def activate_item(
    item_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: InventoryItemService = Depends(Provide[MastersContainer.inventory_item_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    item = await service.activate_item(item_id, updated_by=user_uuid)
    resp_model = InventoryItemResponse.model_validate(item, from_attributes=True)
    resp_model.product_attribute_ids = [attr.id for attr in item.product_attributes]
    return SuccessResponse(data=resp_model)

@router.patch("/{item_id}/deactivate", response_model=SuccessResponse[InventoryItemResponse])
@inject
async def deactivate_item(
    item_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: InventoryItemService = Depends(Provide[MastersContainer.inventory_item_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    item = await service.deactivate_item(item_id, updated_by=user_uuid)
    resp_model = InventoryItemResponse.model_validate(item, from_attributes=True)
    resp_model.product_attribute_ids = [attr.id for attr in item.product_attributes]
    return SuccessResponse(data=resp_model)

@router.patch("/{item_id}/archive", response_model=SuccessResponse[InventoryItemResponse])
@inject
async def archive_item(
    item_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: InventoryItemService = Depends(Provide[MastersContainer.inventory_item_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    item = await service.archive_item(item_id, updated_by=user_uuid)
    resp_model = InventoryItemResponse.model_validate(item, from_attributes=True)
    resp_model.product_attribute_ids = [attr.id for attr in item.product_attributes]
    return SuccessResponse(data=resp_model)
