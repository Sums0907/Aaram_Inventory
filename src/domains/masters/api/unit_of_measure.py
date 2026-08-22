from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser, require_permission
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.unit_of_measure import UnitOfMeasureCreate, UnitOfMeasureUpdate, UnitOfMeasureResponse
from src.domains.masters.services.unit_of_measure import UnitOfMeasureService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/units-of-measure", tags=["Unit of Measure"])

@router.get("", response_model=SuccessResponse[List[UnitOfMeasureResponse]])
@inject
async def list_units(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(require_permission("INVENTORY_CATALOG_VIEW")),
    service: UnitOfMeasureService = Depends(Provide[MastersContainer.unit_of_measure_service])
):
    units = await service.list_units(skip=skip, limit=limit)
    response_data = [UnitOfMeasureResponse.model_validate(unit, from_attributes=True) for unit in units]
    return SuccessResponse(data=response_data)

@router.get("/{unit_id}", response_model=SuccessResponse[UnitOfMeasureResponse])
@inject
async def get_unit(
    unit_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_CATALOG_VIEW")),
    service: UnitOfMeasureService = Depends(Provide[MastersContainer.unit_of_measure_service])
):
    unit = await service.get_unit(unit_id)
    return SuccessResponse(data=UnitOfMeasureResponse.model_validate(unit, from_attributes=True))

@router.post("", response_model=SuccessResponse[UnitOfMeasureResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_unit(
    schema: UnitOfMeasureCreate,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_CREATE")),
    service: UnitOfMeasureService = Depends(Provide[MastersContainer.unit_of_measure_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    unit = await service.create_unit(schema, created_by=user_uuid)
    return SuccessResponse(data=UnitOfMeasureResponse.model_validate(unit, from_attributes=True))

@router.put("/{unit_id}", response_model=SuccessResponse[UnitOfMeasureResponse])
@inject
async def update_unit(
    unit_id: UUID,
    schema: UnitOfMeasureUpdate,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: UnitOfMeasureService = Depends(Provide[MastersContainer.unit_of_measure_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    unit = await service.update_unit(unit_id, schema, updated_by=user_uuid)
    return SuccessResponse(data=UnitOfMeasureResponse.model_validate(unit, from_attributes=True))

@router.patch("/{unit_id}/activate", response_model=SuccessResponse[UnitOfMeasureResponse])
@inject
async def activate_unit(
    unit_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: UnitOfMeasureService = Depends(Provide[MastersContainer.unit_of_measure_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    unit = await service.activate_unit(unit_id, updated_by=user_uuid)
    return SuccessResponse(data=UnitOfMeasureResponse.model_validate(unit, from_attributes=True))

@router.patch("/{unit_id}/deactivate", response_model=SuccessResponse[UnitOfMeasureResponse])
@inject
async def deactivate_unit(
    unit_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: UnitOfMeasureService = Depends(Provide[MastersContainer.unit_of_measure_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    unit = await service.deactivate_unit(unit_id, updated_by=user_uuid)
    return SuccessResponse(data=UnitOfMeasureResponse.model_validate(unit, from_attributes=True))

@router.patch("/{unit_id}/archive", response_model=SuccessResponse[UnitOfMeasureResponse])
@inject
async def archive_unit(
    unit_id: UUID,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_PRODUCT_UPDATE")),
    service: UnitOfMeasureService = Depends(Provide[MastersContainer.unit_of_measure_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    unit = await service.archive_unit(unit_id, updated_by=user_uuid)
    return SuccessResponse(data=UnitOfMeasureResponse.model_validate(unit, from_attributes=True))
