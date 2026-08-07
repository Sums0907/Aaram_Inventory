from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse
from src.app.container import DomainsContainer
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.exception import InventoryExceptionRepository
from src.domains.inventory.repositories.movement import InventoryMovementRepository

router = APIRouter(prefix="/inventory/dashboard", tags=["inventory-dashboard"])

@router.get("/kpis", response_model=SuccessResponse[dict])
@inject
async def get_dashboard_kpis(
    balance_repository: InventoryBalanceRepository = Depends(Provide[DomainsContainer.inventory.balance_repository]),
    movement_repository: InventoryMovementRepository = Depends(Provide[DomainsContainer.inventory.movement_repository])
):
    """
    Returns aggregate KPIs for the Inventory Dashboard.
    """
    kpis = await balance_repository.get_dashboard_kpis()
    manual_adj = await movement_repository.get_manual_adjustments_today_count()
    kpis["manual_adjustments_today"] = manual_adj
    return SuccessResponse(data=kpis)


@router.get("/exceptions", response_model=SuccessResponse[list])
@inject
async def get_dashboard_exceptions(
    exception_repository: InventoryExceptionRepository = Depends(Provide[DomainsContainer.inventory.exception_repository])
):
    """
    Returns a list of open inventory exceptions for the Exceptions Workbench.
    """
    exceptions = await exception_repository.get_all_open_exceptions(limit=50)
    # Serialize the models
    data = [
        {
            "id": str(e.id),
            "exception_number": e.exception_number,
            "sku_id": str(e.sku_id),
            "warehouse_id": str(e.warehouse_id),
            "status": e.status,
            "resolution_notes": e.resolution_notes,
            "exception_date": e.exception_date.isoformat(),
            "expected_quantity": e.expected_quantity,
            "actual_quantity": e.actual_quantity,
            "difference": e.difference
        }
        for e in exceptions
    ]
    return SuccessResponse(data=data)
