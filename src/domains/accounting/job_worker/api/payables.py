from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject
from uuid import UUID
from src.foundation.api.responses import SuccessResponse
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.app.container import DomainsContainer
from src.domains.accounting.job_worker.services.payable_service import PayableService
from src.domains.accounting.job_worker.schemas.payable import (
    JobWorkerPayableLedgerResponse, PayableDashboardResponse
)

router = APIRouter(prefix="/job-worker-accounting", tags=["Job Worker Payables"])


@router.get("/dashboard", response_model=SuccessResponse[PayableDashboardResponse])
@inject
async def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    service: PayableService = Depends(Provide[DomainsContainer.accounting.jw_payable_service]),
):
    from sqlalchemy import select
    from src.domains.masters.models.supplier import Supplier

    session = service.payable_repo.session
    stmt = select(Supplier).where(Supplier.is_job_worker == True)
    res = await session.execute(stmt)
    workers = res.scalars().all()
    job_workers = [(jw.id, jw.name) for jw in workers]

    dashboard = await service.get_dashboard(job_workers)
    return SuccessResponse(data=dashboard)


@router.get("/worker/{job_worker_id}/ledger", response_model=SuccessResponse[JobWorkerPayableLedgerResponse])
@inject
async def get_payable_ledger(
    job_worker_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: PayableService = Depends(Provide[DomainsContainer.accounting.jw_payable_service]),
):
    from sqlalchemy import select
    from src.domains.masters.models.supplier import Supplier

    session = service.payable_repo.session
    stmt = select(Supplier).where(Supplier.id == job_worker_id)
    res = await session.execute(stmt)
    worker = res.scalars().first()
    name = worker.name if worker else str(job_worker_id)

    ledger = await service.get_payable_ledger(job_worker_id, name)
    return SuccessResponse(data=ledger)
