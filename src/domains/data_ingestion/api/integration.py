from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.data_ingestion.schemas.integration import IntegrationCreate, IntegrationUpdate, IntegrationResponse
from src.domains.data_ingestion.services.integration import IntegrationService
from src.domains.data_ingestion.dependency_injection import DataIngestionContainer

router = APIRouter(prefix="/integrations", tags=["Integration"])

@router.get("", response_model=SuccessResponse[List[IntegrationResponse]])
@inject
async def list_integrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[DataIngestionContainer.integration_service])
):
    integrations = await service.list_integrations(skip=skip, limit=limit)
    response_data = [IntegrationResponse.model_validate(item, from_attributes=True) for item in integrations]
    return SuccessResponse(data=response_data)

@router.get("/{integration_id}", response_model=SuccessResponse[IntegrationResponse])
@inject
async def get_integration(
    integration_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[DataIngestionContainer.integration_service])
):
    integration = await service.get_integration(integration_id)
    return SuccessResponse(data=IntegrationResponse.model_validate(integration, from_attributes=True))

@router.post("", response_model=SuccessResponse[IntegrationResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_integration(
    schema: IntegrationCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[DataIngestionContainer.integration_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    integration = await service.create_integration(schema, created_by=user_uuid)
    return SuccessResponse(data=IntegrationResponse.model_validate(integration, from_attributes=True))

@router.put("/{integration_id}", response_model=SuccessResponse[IntegrationResponse])
@inject
async def update_integration(
    integration_id: UUID,
    schema: IntegrationUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[DataIngestionContainer.integration_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    integration = await service.update_integration(integration_id, schema, updated_by=user_uuid)
    return SuccessResponse(data=IntegrationResponse.model_validate(integration, from_attributes=True))

@router.patch("/{integration_id}/activate", response_model=SuccessResponse[IntegrationResponse])
@inject
async def activate_integration(
    integration_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[DataIngestionContainer.integration_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    integration = await service.activate_integration(integration_id, updated_by=user_uuid)
    return SuccessResponse(data=IntegrationResponse.model_validate(integration, from_attributes=True))

@router.patch("/{integration_id}/deactivate", response_model=SuccessResponse[IntegrationResponse])
@inject
async def deactivate_integration(
    integration_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[DataIngestionContainer.integration_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    integration = await service.deactivate_integration(integration_id, updated_by=user_uuid)
    return SuccessResponse(data=IntegrationResponse.model_validate(integration, from_attributes=True))

@router.patch("/{integration_id}/archive", response_model=SuccessResponse[IntegrationResponse])
@inject
async def archive_integration(
    integration_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: IntegrationService = Depends(Provide[DataIngestionContainer.integration_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    integration = await service.archive_integration(integration_id, updated_by=user_uuid)
    return SuccessResponse(data=IntegrationResponse.model_validate(integration, from_attributes=True))
