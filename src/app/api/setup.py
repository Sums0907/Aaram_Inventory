from uuid import UUID
from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.company import CompanyCreate, CompanyResponse
from src.domains.masters.services.company import CompanyService
from src.app.container import DomainsContainer

router = APIRouter(tags=["Installation & Setup"])

@router.post("/company", response_model=SuccessResponse[CompanyResponse], status_code=status.HTTP_201_CREATED)
@inject
async def setup_company(
    schema: CompanyCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: CompanyService = Depends(Provide[DomainsContainer.masters.company_service])
):
    """
    Internal setup API to create the root Company.
    Isolated from the Masters domain APIs because setup is an installation operation,
    not a standard business capability.
    """
    user_uuid = UUID(current_user.id)
    company = await service.create_company(schema, created_by=user_uuid)
    return SuccessResponse(data=CompanyResponse.model_validate(company, from_attributes=True))
