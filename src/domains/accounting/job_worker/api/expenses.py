from fastapi import APIRouter, Depends, Query, status
from dependency_injector.wiring import Provide, inject
from uuid import UUID
from typing import List
from src.foundation.api.responses import SuccessResponse
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.app.container import DomainsContainer
from src.domains.accounting.job_worker.services.expense_service import ExpenseService
from src.domains.accounting.job_worker.schemas.job_work_expense import (
    JobWorkExpenseCreate, JobWorkExpenseResponse
)

router = APIRouter(prefix="/job-worker-accounting/expenses", tags=["Job Work Expenses"])


@router.post("", response_model=SuccessResponse[JobWorkExpenseResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_expense(
    schema: JobWorkExpenseCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: ExpenseService = Depends(Provide[DomainsContainer.accounting.jw_expense_service]),
):
    from uuid import UUID as _UUID
    expense = await service.create_manual(schema, created_by=_UUID(current_user.id))
    return SuccessResponse(
        data=JobWorkExpenseResponse.model_validate(expense, from_attributes=True),
        message="Expense created.",
    )


@router.get("", response_model=SuccessResponse[List[JobWorkExpenseResponse]])
@inject
async def list_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user),
    service: ExpenseService = Depends(Provide[DomainsContainer.accounting.jw_expense_service]),
):
    expenses = await service.get_all(skip, limit)
    return SuccessResponse(data=[
        JobWorkExpenseResponse.model_validate(e, from_attributes=True) for e in expenses
    ])


@router.get("/worker/{job_worker_id}", response_model=SuccessResponse[List[JobWorkExpenseResponse]])
@inject
async def list_expenses_for_worker(
    job_worker_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ExpenseService = Depends(Provide[DomainsContainer.accounting.jw_expense_service]),
):
    expenses = await service.get_all_for_worker(job_worker_id)
    return SuccessResponse(data=[
        JobWorkExpenseResponse.model_validate(e, from_attributes=True) for e in expenses
    ])
