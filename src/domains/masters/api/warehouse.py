from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from src.domains.masters.services.warehouse import WarehouseService
from src.app.container import DomainsContainer

router = APIRouter(prefix="/warehouses", tags=["Warehouse"])

@router.get("", response_model=SuccessResponse[List[WarehouseResponse]])
@inject
async def list_warehouses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(Provide[DomainsContainer.masters.warehouse_service])
):
    warehouses = await service.list_warehouses(skip=skip, limit=limit)
    response_data = [WarehouseResponse.model_validate(w, from_attributes=True) for w in warehouses]
    return SuccessResponse(data=response_data)

@router.get("/{warehouse_id}", response_model=SuccessResponse[WarehouseResponse])
@inject
async def get_warehouse(
    warehouse_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(Provide[DomainsContainer.masters.warehouse_service])
):
    warehouse = await service.get_warehouse(warehouse_id)
    return SuccessResponse(data=WarehouseResponse.model_validate(warehouse, from_attributes=True))

@router.post("", response_model=SuccessResponse[WarehouseResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_warehouse(
    schema: WarehouseCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(Provide[DomainsContainer.masters.warehouse_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    warehouse = await service.create_warehouse(schema, created_by=user_uuid)
    return SuccessResponse(data=WarehouseResponse.model_validate(warehouse, from_attributes=True))

@router.put("/{warehouse_id}", response_model=SuccessResponse[WarehouseResponse])
@inject
async def update_warehouse(
    warehouse_id: UUID,
    schema: WarehouseUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(Provide[DomainsContainer.masters.warehouse_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    warehouse = await service.update_warehouse(warehouse_id, schema, updated_by=user_uuid)
    return SuccessResponse(data=WarehouseResponse.model_validate(warehouse, from_attributes=True))

@router.patch("/{warehouse_id}/activate", response_model=SuccessResponse[WarehouseResponse])
@inject
async def activate_warehouse(
    warehouse_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(Provide[DomainsContainer.masters.warehouse_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    warehouse = await service.activate_warehouse(warehouse_id, updated_by=user_uuid)
    return SuccessResponse(data=WarehouseResponse.model_validate(warehouse, from_attributes=True))

@router.patch("/{warehouse_id}/deactivate", response_model=SuccessResponse[WarehouseResponse])
@inject
async def deactivate_warehouse(
    warehouse_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(Provide[DomainsContainer.masters.warehouse_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    warehouse = await service.deactivate_warehouse(warehouse_id, updated_by=user_uuid)
    return SuccessResponse(data=WarehouseResponse.model_validate(warehouse, from_attributes=True))

@router.patch("/{warehouse_id}/archive", response_model=SuccessResponse[WarehouseResponse])
@inject
async def archive_warehouse(
    warehouse_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(Provide[DomainsContainer.masters.warehouse_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    warehouse = await service.archive_warehouse(warehouse_id, updated_by=user_uuid)
    return SuccessResponse(data=WarehouseResponse.model_validate(warehouse, from_attributes=True))
