from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import require_permission

from src.foundation.api.responses import SuccessResponse
from src.app.container import DomainsContainer
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.exception import InventoryExceptionRepository
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.repositories.job_work import JobWorkRepository
from src.domains.masters.repositories.sku import SKURepository

router = APIRouter(prefix="/inventory/dashboard", tags=["inventory-dashboard"])

@router.get("/kpis", response_model=SuccessResponse[dict])
@inject
async def get_dashboard_kpis(
    balance_repository: InventoryBalanceRepository = Depends(Provide[DomainsContainer.inventory.balance_repository]),
    movement_repository: InventoryMovementRepository = Depends(Provide[DomainsContainer.inventory.movement_repository]),
    sku_repository: SKURepository = Depends(Provide[DomainsContainer.masters.sku_repository]),
    job_work_repository: JobWorkRepository = Depends(Provide[DomainsContainer.inventory.job_work_repository]),
    _=Depends(require_permission("INVENTORY_CATALOG_VIEW"))
):
    """
    Returns aggregate KPIs for the Inventory Dashboard.
    """
    kpis = await balance_repository.get_dashboard_kpis()
    manual_adj = await movement_repository.get_manual_adjustments_today_count()
    kpis["manual_adjustments_today"] = manual_adj
    
    bom_kpis = await sku_repository.get_bom_health_kpi()
    kpis["bom_health"] = bom_kpis
    
    pending_jw = await job_work_repository.get_total_pending_stock_kpi()
    kpis["total_pending_job_work"] = pending_jw
    
    return SuccessResponse(data=kpis)


@router.get("/exceptions", response_model=SuccessResponse[list])
@inject
async def get_dashboard_exceptions(
    exception_repository: InventoryExceptionRepository = Depends(Provide[DomainsContainer.inventory.exception_repository]),
    _=Depends(require_permission("INVENTORY_CATALOG_VIEW"))
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


@router.get("/recent-activity", response_model=SuccessResponse[list])
@inject
async def get_dashboard_recent_activity(
    movement_repository: InventoryMovementRepository = Depends(Provide[DomainsContainer.inventory.movement_repository]),
    _=Depends(require_permission("INVENTORY_CATALOG_VIEW"))
):
    """
    Returns a feed of recent inventory activity for the dashboard.
    """
    movements = await movement_repository.get_recent_movements(limit=20)
    data = [
        {
            "id": str(m.id),
            "movement_number": m.movement_number,
            "sku_id": str(m.sku_id),
            "quantity": float(m.quantity),
            "movement_type": m.movement_type,
            "reference_number": m.reference_number,
            "status": m.status,
            "posting_date": m.posting_date.isoformat() if m.posting_date else None,
            "created_on": m.created_on.isoformat()
        }
        for m in movements
    ]
    return SuccessResponse(data=data)
