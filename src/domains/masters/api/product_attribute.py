from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.product_attribute import ProductAttributeCreate, ProductAttributeUpdate, ProductAttributeResponse
from src.domains.masters.services.product_attribute import ProductAttributeService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/product-attributes", tags=["Product Attribute"])

@router.get("", response_model=SuccessResponse[List[ProductAttributeResponse]])
@inject
async def list_attributes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductAttributeService = Depends(Provide[MastersContainer.product_attribute_service])
):
    attributes = await service.list_attributes(skip=skip, limit=limit)
    response_data = [ProductAttributeResponse.model_validate(a, from_attributes=True) for a in attributes]
    return SuccessResponse(data=response_data)

@router.get("/{attribute_id}", response_model=SuccessResponse[ProductAttributeResponse])
@inject
async def get_attribute(
    attribute_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductAttributeService = Depends(Provide[MastersContainer.product_attribute_service])
):
    attribute = await service.get_attribute(attribute_id)
    return SuccessResponse(data=ProductAttributeResponse.model_validate(attribute, from_attributes=True))

@router.post("", response_model=SuccessResponse[ProductAttributeResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_attribute(
    schema: ProductAttributeCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductAttributeService = Depends(Provide[MastersContainer.product_attribute_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    attribute = await service.create_attribute(schema, created_by=user_uuid)
    return SuccessResponse(data=ProductAttributeResponse.model_validate(attribute, from_attributes=True))

@router.put("/{attribute_id}", response_model=SuccessResponse[ProductAttributeResponse])
@inject
async def update_attribute(
    attribute_id: UUID,
    schema: ProductAttributeUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductAttributeService = Depends(Provide[MastersContainer.product_attribute_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    attribute = await service.update_attribute(attribute_id, schema, updated_by=user_uuid)
    return SuccessResponse(data=ProductAttributeResponse.model_validate(attribute, from_attributes=True))

@router.patch("/{attribute_id}/activate", response_model=SuccessResponse[ProductAttributeResponse])
@inject
async def activate_attribute(
    attribute_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductAttributeService = Depends(Provide[MastersContainer.product_attribute_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    attribute = await service.activate_attribute(attribute_id, updated_by=user_uuid)
    return SuccessResponse(data=ProductAttributeResponse.model_validate(attribute, from_attributes=True))

@router.patch("/{attribute_id}/deactivate", response_model=SuccessResponse[ProductAttributeResponse])
@inject
async def deactivate_attribute(
    attribute_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductAttributeService = Depends(Provide[MastersContainer.product_attribute_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    attribute = await service.deactivate_attribute(attribute_id, updated_by=user_uuid)
    return SuccessResponse(data=ProductAttributeResponse.model_validate(attribute, from_attributes=True))

@router.patch("/{attribute_id}/archive", response_model=SuccessResponse[ProductAttributeResponse])
@inject
async def archive_attribute(
    attribute_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductAttributeService = Depends(Provide[MastersContainer.product_attribute_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    attribute = await service.archive_attribute(attribute_id, updated_by=user_uuid)
    return SuccessResponse(data=ProductAttributeResponse.model_validate(attribute, from_attributes=True))
