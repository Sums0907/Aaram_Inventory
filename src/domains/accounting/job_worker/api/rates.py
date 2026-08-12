from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import Provide, inject
from uuid import UUID
from typing import List
from src.foundation.api.responses import SuccessResponse
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.app.container import DomainsContainer
from src.domains.accounting.job_worker.services.rate_service import RateService
from src.domains.accounting.job_worker.schemas.job_work_rate import (
    JobWorkRateCreate, JobWorkRateResponse
)

router = APIRouter(prefix="/job-worker-accounting/rates", tags=["Job Worker Rates"])


@router.post("", response_model=SuccessResponse[JobWorkRateResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_rate(
    schema: JobWorkRateCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: RateService = Depends(Provide[DomainsContainer.accounting.jw_rate_service]),
):
    from uuid import UUID as _UUID
    rate = await service.create_rate(schema, created_by=_UUID(current_user.id))
    return SuccessResponse(
        data=JobWorkRateResponse.model_validate(rate, from_attributes=True),
        message="Job Work Rate created.",
    )


@router.get("", response_model=SuccessResponse[List[JobWorkRateResponse]])
@inject
async def list_rates(
    current_user: CurrentUser = Depends(get_current_user),
    service: RateService = Depends(Provide[DomainsContainer.accounting.jw_rate_service]),
):
    rates = await service.get_all()
    return SuccessResponse(data=[
        JobWorkRateResponse.model_validate(r, from_attributes=True) for r in rates
    ])


@router.get("/worker/{job_worker_id}", response_model=SuccessResponse[List[JobWorkRateResponse]])
@inject
async def list_rates_for_worker(
    job_worker_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: RateService = Depends(Provide[DomainsContainer.accounting.jw_rate_service]),
):
    rates = await service.get_all_for_worker(job_worker_id)
    return SuccessResponse(data=[
        JobWorkRateResponse.model_validate(r, from_attributes=True) for r in rates
    ])


@router.delete("/{rate_id}", response_model=SuccessResponse[JobWorkRateResponse])
@inject
async def deactivate_rate(
    rate_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: RateService = Depends(Provide[DomainsContainer.accounting.jw_rate_service]),
):
    from uuid import UUID as _UUID
    rate = await service.deactivate_rate(rate_id, updated_by=_UUID(current_user.id))
    return SuccessResponse(
        data=JobWorkRateResponse.model_validate(rate, from_attributes=True),
        message="Rate deactivated.",
    )
