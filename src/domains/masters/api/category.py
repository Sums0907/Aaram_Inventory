from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser, require_permission
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from src.domains.masters.services.category import CategoryService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/categories", tags=["Category"])

@router.get("", response_model=SuccessResponse[List[CategoryResponse]])
@inject
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    item_type: Optional[str] = Query(None, description="Filter by Item Type"),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_CATALOG_VIEW")),
    service: CategoryService = Depends(Provide[MastersContainer.category_service])
):
    categories = await service.list_categories(skip=skip, limit=limit, item_type=item_type)
    response_data = [CategoryResponse.model_validate(c, from_attributes=True) for c in categories]
    return SuccessResponse(data=response_data)

@router.get("/{category_id}", response_model=SuccessResponse[CategoryResponse])
@inject
async def get_category(
    category_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_CATALOG_VIEW")),
    service: CategoryService = Depends(Provide[MastersContainer.category_service])
):
    category = await service.get_category(category_id)
    return SuccessResponse(data=CategoryResponse.model_validate(category, from_attributes=True))

@router.post("", response_model=SuccessResponse[CategoryResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_category(
    schema: CategoryCreate,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_CREATE")),
    service: CategoryService = Depends(Provide[MastersContainer.category_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    category = await service.create_category(schema, created_by=user_uuid)
    return SuccessResponse(data=CategoryResponse.model_validate(category, from_attributes=True))

@router.put("/{category_id}", response_model=SuccessResponse[CategoryResponse])
@inject
async def update_category(
    category_id: UUID,
    schema: CategoryUpdate,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: CategoryService = Depends(Provide[MastersContainer.category_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    category = await service.update_category(category_id, schema, updated_by=user_uuid)
    return SuccessResponse(data=CategoryResponse.model_validate(category, from_attributes=True))

@router.patch("/{category_id}/activate", response_model=SuccessResponse[CategoryResponse])
@inject
async def activate_category(
    category_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: CategoryService = Depends(Provide[MastersContainer.category_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    category = await service.activate_category(category_id, updated_by=user_uuid)
    return SuccessResponse(data=CategoryResponse.model_validate(category, from_attributes=True))

@router.patch("/{category_id}/deactivate", response_model=SuccessResponse[CategoryResponse])
@inject
async def deactivate_category(
    category_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: CategoryService = Depends(Provide[MastersContainer.category_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    category = await service.deactivate_category(category_id, updated_by=user_uuid)
    return SuccessResponse(data=CategoryResponse.model_validate(category, from_attributes=True))

@router.patch("/{category_id}/archive", response_model=SuccessResponse[CategoryResponse])
@inject
async def archive_category(
    category_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: CategoryService = Depends(Provide[MastersContainer.category_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    category = await service.archive_category(category_id, updated_by=user_uuid)
    return SuccessResponse(data=CategoryResponse.model_validate(category, from_attributes=True))

@router.delete("/{category_id}", response_model=SuccessResponse[None])
@inject
async def delete_category(
    category_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: CategoryService = Depends(Provide[MastersContainer.category_service])
):
    await service.delete_category(category_id)
    return SuccessResponse(data=None, message="Category permanently deleted")
