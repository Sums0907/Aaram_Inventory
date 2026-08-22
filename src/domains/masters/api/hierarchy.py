from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser, require_permission
from src.foundation.api.responses import SuccessResponse
from src.domains.masters.schemas.hierarchy import HierarchyResponse
from src.domains.masters.services.hierarchy import InventoryHierarchyService
from src.domains.masters.dependency_injection import MastersContainer

router = APIRouter(prefix="/hierarchy", tags=["Inventory Hierarchy"])

@router.get("", response_model=SuccessResponse[HierarchyResponse], status_code=status.HTTP_200_OK)
@inject
async def get_hierarchy(
    only_archived: bool = False,
    current_user: CurrentUser = Depends(require_permission("INVENTORY_CATALOG_VIEW")),
    service: InventoryHierarchyService = Depends(Provide[MastersContainer.inventory_hierarchy_service])
):
    data = await service.get_hierarchy(only_archived)
    return SuccessResponse(data=data)
