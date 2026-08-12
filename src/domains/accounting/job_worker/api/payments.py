from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import Provide, inject
from uuid import UUID
from typing import List
from src.foundation.api.responses import SuccessResponse
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.app.container import DomainsContainer
from src.domains.accounting.job_worker.services.payment_service import PaymentService
from src.domains.accounting.job_worker.schemas.job_worker_payment import (
    JobWorkerPaymentCreate, JobWorkerPaymentResponse
)

router = APIRouter(prefix="/job-worker-accounting/payments", tags=["Job Worker Payments"])


@router.post("", response_model=SuccessResponse[JobWorkerPaymentResponse], status_code=status.HTTP_201_CREATED)
@inject
async def record_payment(
    schema: JobWorkerPaymentCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: PaymentService = Depends(Provide[DomainsContainer.accounting.jw_payment_service]),
):
    from uuid import UUID as _UUID
    payment = await service.record_payment(schema, created_by=_UUID(current_user.id))
    return SuccessResponse(
        data=JobWorkerPaymentResponse.model_validate(payment, from_attributes=True),
        message="Payment recorded.",
    )


@router.get("", response_model=SuccessResponse[List[JobWorkerPaymentResponse]])
@inject
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    service: PaymentService = Depends(Provide[DomainsContainer.accounting.jw_payment_service]),
):
    payments = await service.get_all(skip, limit)
    return SuccessResponse(data=[
        JobWorkerPaymentResponse.model_validate(p, from_attributes=True) for p in payments
    ])


@router.get("/worker/{job_worker_id}", response_model=SuccessResponse[List[JobWorkerPaymentResponse]])
@inject
async def list_payments_for_worker(
    job_worker_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: PaymentService = Depends(Provide[DomainsContainer.accounting.jw_payment_service]),
):
    payments = await service.get_all_for_worker(job_worker_id)
    return SuccessResponse(data=[
        JobWorkerPaymentResponse.model_validate(p, from_attributes=True) for p in payments
    ])
