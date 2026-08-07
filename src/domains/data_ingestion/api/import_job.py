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
    response_data = []
    for item in jobs:
        resp = ImportJobResponse.model_validate(item, from_attributes=True)
        if item.import_file:
            resp.file_path = item.import_file.file_name
        response_data.append(resp)
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

from src.domains.data_ingestion.schemas.import_job import ImportJobPreviewResponse
from src.domains.data_ingestion.repositories.import_record import ImportRecordRepository
@router.get("/{job_id}/preview", response_model=SuccessResponse[ImportJobPreviewResponse])
@inject
async def get_import_job_preview(
    job_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    record_repo: ImportRecordRepository = Depends(Provide[DataIngestionContainer.import_record_repository])
):
    records = await record_repo.get_by_job_id(job_id, limit=10000)
    
    total_orders = 0
    skus = set()
    units_sold = 0
    units_returned = 0
    dates = []
    
    for r in records:
        if r.record_type == "SALES_ORDER":
            total_orders += 1
            data = r.normalized_data
            order_date_str = data.get("order_date")
            if order_date_str:
                dates.append(order_date_str)
                
            status = str(data.get("status", "")).upper()
            
            for item in data.get("items", []):
                sku_code = item.get("external_sku_code")
                qty = item.get("quantity", 0)
                
                if sku_code:
                    skus.add(sku_code)
                    
                if "RETURN" in status:
                    units_returned += qty
                else:
                    units_sold += qty

    dates.sort()
    
    return SuccessResponse(data=ImportJobPreviewResponse(
        report_date_min=dates[0] if dates else None,
        report_date_max=dates[-1] if dates else None,
        total_orders=total_orders,
        total_skus=len(skus),
        units_sold=units_sold,
        units_returned=units_returned
    ))
