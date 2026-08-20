from uuid import UUID
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser, require_permission
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from src.domains.masters.services.company import CompanyService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/companies", tags=["Company"])

@router.get("/{company_id}", response_model=SuccessResponse[CompanyResponse])
@inject
async def get_company(
    company_id: UUID,
    current_user: CurrentUser = Depends(require_permission("CATALOG_VIEW")),
    service: CompanyService = Depends(Provide[MastersContainer.company_service])
):
    company = await service.get_company(company_id)
    return SuccessResponse(data=CompanyResponse.model_validate(company, from_attributes=True))

@router.put("/{company_id}", response_model=SuccessResponse[CompanyResponse])
@inject
async def update_company(
    company_id: UUID,
    schema: CompanyUpdate,
    current_user: CurrentUser = Depends(require_permission("PRODUCT_UPDATE")),
    service: CompanyService = Depends(Provide[MastersContainer.company_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    company = await service.update_company(company_id, schema, updated_by=user_uuid)
    return SuccessResponse(data=CompanyResponse.model_validate(company, from_attributes=True))

@router.patch("/{company_id}/activate", response_model=SuccessResponse[CompanyResponse])
@inject
async def activate_company(
    company_id: UUID,
    current_user: CurrentUser = Depends(require_permission("PRODUCT_UPDATE")),
    service: CompanyService = Depends(Provide[MastersContainer.company_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    company = await service.activate_company(company_id, updated_by=user_uuid)
    return SuccessResponse(data=CompanyResponse.model_validate(company, from_attributes=True))

@router.patch("/{company_id}/deactivate", response_model=SuccessResponse[CompanyResponse])
@inject
async def deactivate_company(
    company_id: UUID,
    current_user: CurrentUser = Depends(require_permission("PRODUCT_UPDATE")),
    service: CompanyService = Depends(Provide[MastersContainer.company_service])
):
    from uuid import UUID
    user_uuid = UUID(current_user.id)
    company = await service.deactivate_company(company_id, updated_by=user_uuid)
    return SuccessResponse(data=CompanyResponse.model_validate(company, from_attributes=True))
