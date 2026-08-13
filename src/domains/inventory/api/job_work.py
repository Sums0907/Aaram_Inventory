from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
import uuid
from typing import List, Callable, AsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession
from src.foundation.api.responses import SuccessResponse
from src.app.container import DomainsContainer
from src.domains.inventory.services.job_work import JobWorkService
from src.domains.inventory.schemas.job_work import (
    JobWorkIssueCreate,
    JobWorkIssueResponse,
    JobWorkReturnCreate,
    JobWorkReturnResponse,
    JobWorkerInventoryResponse,
    InventoryTransformationRecordResponse,
    JobWorkerPendingStockResponse,
    StockCustodyLedgerResponse
)
from src.domains.inventory.services.transformation_engine import InventoryTransformationEngine
from typing import Optional

router = APIRouter(prefix="/inventory", tags=["inventory-job-works"])

@router.post("/job-works/issues", response_model=SuccessResponse[JobWorkIssueResponse])
@inject
async def issue_material(
    request: JobWorkIssueCreate,
    service: JobWorkService = Depends(Provide[DomainsContainer.inventory.job_work_service])
):
    sys_user = uuid.UUID("00000000-0000-0000-0000-000000000001")
    issue = await service.issue_material(request, sys_user)
    return SuccessResponse(data=issue)

@router.post("/job-works/returns", response_model=SuccessResponse[JobWorkReturnResponse])
@inject
async def return_material(
    request: JobWorkReturnCreate,
    service: JobWorkService = Depends(Provide[DomainsContainer.inventory.job_work_service])
):
    sys_user = uuid.UUID("00000000-0000-0000-0000-000000000001")
    job_return = await service.return_material(request, sys_user)
    return SuccessResponse(data=job_return)

@router.get("/job-works/suppliers/{supplier_id}/pending-stock", response_model=SuccessResponse[List[JobWorkerInventoryResponse]])
@inject
async def get_pending_stock(
    supplier_id: uuid.UUID,
    service: JobWorkService = Depends(Provide[DomainsContainer.inventory.job_work_service])
):
    stock = await service.get_pending_stock(supplier_id)
    return SuccessResponse(data=stock)

@router.get("/job-works/pending-stock", response_model=SuccessResponse[JobWorkerPendingStockResponse])
@inject
async def get_all_pending_stock(
    service: JobWorkService = Depends(Provide[DomainsContainer.inventory.job_work_service])
):
    items = await service.get_all_pending_stock()
    kpis = await service.get_pending_stock_kpis()
    return SuccessResponse(data={"items": items, "kpis": kpis})

@router.get("/job-works/suppliers/{supplier_id}/custody-ledger", response_model=SuccessResponse[StockCustodyLedgerResponse])
@inject
async def get_custody_ledger(
    supplier_id: uuid.UUID,
    item_id: Optional[uuid.UUID] = None,
    service: JobWorkService = Depends(Provide[DomainsContainer.inventory.job_work_service])
):
    ledger = await service.get_custody_ledger(supplier_id, item_id)
    return SuccessResponse(data=ledger)

@router.get("/job-works/suppliers/{supplier_id}/activities")
@inject
async def get_job_worker_activities(
    supplier_id: uuid.UUID,
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory])
):
    from sqlalchemy import select, or_, and_
    from src.domains.inventory.models.movement import InventoryMovementModel
    
    # We want movements linked to this job worker:
    # - JOB_WORK_ISSUE, JOB_WORK_RETURN, RAW_MATERIAL_CONSUMPTION
    # For now, just query all movements where reference_id == supplier_id or something similar.
    # Actually, we know the movement types:
    stmt = select(InventoryMovementModel).where(
        InventoryMovementModel.reference_id == supplier_id,
        InventoryMovementModel.movement_type.in_([
            "JOB_WORK_ISSUE", 
            "JOB_WORK_RETURN", 
            "RAW_MATERIAL_CONSUMPTION", 
            "JOB_WORK_RECEIPT"
        ])
    ).order_by(InventoryMovementModel.created_on.desc()).limit(50)
    
    async with session_factory() as session:
        res = await session.execute(stmt)
        records = res.scalars().all()
    
    data = []
    for r in records:
        data.append({
            "id": str(r.id) if r.id else None,
            "movement_type": r.movement_type,
            "sku_id": str(r.sku_id) if r.sku_id else None,
            "quantity": r.quantity,
            "reference_id": str(r.reference_id) if r.reference_id else None,
            "reference_number": r.reference_number,
            "movement_date": r.movement_date.isoformat() if r.movement_date else None,
            "created_on": r.created_on.isoformat() if r.created_on else None
        })
    
    return SuccessResponse(data=data)

@router.get("/job-works/activities")
@inject
async def get_all_job_work_activities(
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory])
):
    from sqlalchemy import select
    from src.domains.inventory.models.movement import InventoryMovementModel
    
    stmt = select(InventoryMovementModel).where(
        InventoryMovementModel.movement_type.in_([
            "JOB_WORK_ISSUE", 
            "JOB_WORK_RETURN", 
            "RAW_MATERIAL_CONSUMPTION", 
            "JOB_WORK_RECEIPT"
        ])
    ).order_by(InventoryMovementModel.created_on.desc()).limit(100)
    
    async with session_factory() as session:
        res = await session.execute(stmt)
        records = res.scalars().all()
    
    data = []
    for r in records:
        data.append({
            "id": str(r.id) if r.id else None,
            "movement_type": r.movement_type,
            "sku_id": str(r.sku_id) if r.sku_id else None,
            "quantity": r.quantity,
            "reference_id": str(r.reference_id) if r.reference_id else None,
            "reference_number": r.reference_number,
            "movement_date": r.movement_date.isoformat() if r.movement_date else None,
            "created_on": r.created_on.isoformat() if r.created_on else None
        })
    
    return SuccessResponse(data=data)

@router.get("/transformations", response_model=SuccessResponse[List[InventoryTransformationRecordResponse]])
@inject
async def get_transformations(
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory])
):
    from src.domains.inventory.models.job_work import InventoryTransformationRecord
    from sqlalchemy import select
    # Inline quick implementation for listing records
    stmt = select(InventoryTransformationRecord)
    async with session_factory() as session:
        res = await session.execute(stmt)
        records = res.scalars().all()
    return SuccessResponse(data=records)
