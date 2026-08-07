from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from src.domains.masters.services.product import ProductService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/products", tags=["Product"])

@router.get("", response_model=SuccessResponse[List[ProductResponse]])
@inject
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductService = Depends(Provide[MastersContainer.product_service])
):
    products = await service.list_products(skip=skip, limit=limit)
    response_data = [ProductResponse.model_validate(product, from_attributes=True) for product in products]
    return SuccessResponse(data=response_data)

@router.get("/{product_id}", response_model=SuccessResponse[ProductResponse])
@inject
async def get_product(
    product_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductService = Depends(Provide[MastersContainer.product_service])
):
    product = await service.get_product(product_id)
    return SuccessResponse(data=ProductResponse.model_validate(product, from_attributes=True))

@router.post("", response_model=SuccessResponse[ProductResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_product(
    schema: ProductCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductService = Depends(Provide[MastersContainer.product_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    product = await service.create_product(schema, created_by=user_uuid)
    return SuccessResponse(data=ProductResponse.model_validate(product, from_attributes=True))

@router.put("/{product_id}", response_model=SuccessResponse[ProductResponse])
@inject
async def update_product(
    product_id: UUID,
    schema: ProductUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductService = Depends(Provide[MastersContainer.product_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    product = await service.update_product(product_id, schema, updated_by=user_uuid)
    return SuccessResponse(data=ProductResponse.model_validate(product, from_attributes=True))

@router.patch("/{product_id}/activate", response_model=SuccessResponse[ProductResponse])
@inject
async def activate_product(
    product_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductService = Depends(Provide[MastersContainer.product_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    product = await service.activate_product(product_id, updated_by=user_uuid)
    return SuccessResponse(data=ProductResponse.model_validate(product, from_attributes=True))

@router.patch("/{product_id}/deactivate", response_model=SuccessResponse[ProductResponse])
@inject
async def deactivate_product(
    product_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductService = Depends(Provide[MastersContainer.product_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    product = await service.deactivate_product(product_id, updated_by=user_uuid)
    return SuccessResponse(data=ProductResponse.model_validate(product, from_attributes=True))

@router.patch("/{product_id}/archive", response_model=SuccessResponse[ProductResponse])
@inject
async def archive_product(
    product_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ProductService = Depends(Provide[MastersContainer.product_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    product = await service.archive_product(product_id, updated_by=user_uuid)
    return SuccessResponse(data=ProductResponse.model_validate(product, from_attributes=True))
