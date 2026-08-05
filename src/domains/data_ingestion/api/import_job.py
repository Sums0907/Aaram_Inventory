from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import Provide, inject
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.data_ingestion.schemas.import_job import ImportJobResponse
from src.domains.data_ingestion.services.import_job import ImportJobService
from src.domains.data_ingestion.dependency_injection import DataIngestionContainer

router = APIRouter(prefix="/import-jobs", tags=["Data Ingestion Pipeline"])

@router.get("", response_model=SuccessResponse[List[ImportJobResponse]])
@inject
async def list_import_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: CurrentUser = Depends(get_current_user),
    service: ImportJobService = Depends(Provide[DataIngestionContainer.import_job_service])
):
    jobs = await service.list_jobs(skip=skip, limit=limit)
    response_data = [ImportJobResponse.model_validate(item, from_attributes=True) for item in jobs]
    return SuccessResponse(data=response_data)

@router.get("/{job_id}", response_model=SuccessResponse[ImportJobResponse])
@inject
async def get_import_job(
    job_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: ImportJobService = Depends(Provide[DataIngestionContainer.import_job_service])
):
    job = await service.get_job(job_id)
    return SuccessResponse(data=ImportJobResponse.model_validate(job, from_attributes=True))
