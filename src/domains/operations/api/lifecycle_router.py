from fastapi import APIRouter, Depends, UploadFile, File
from datetime import date
from typing import Optional
from pydantic import BaseModel
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse
from src.app.container import DomainsContainer
from src.domains.operations.services.reconciliation_orchestrator import ReconciliationOrchestratorService, ReconciliationSummary
from src.domains.data_ingestion.services.adapters.shopdeck_order import ShopDeckOrderReader, ShopDeckOrderValidator, ShopDeckOrderMapper
from src.domains.operations.services.report_window import ShopDeckReportWindowService
from src.domains.operations.schemas.lifecycle import DynamicReportWindowResponse

router = APIRouter(prefix="/lifecycle", tags=["Operations - Lifecycle"])

@router.get("/shopdeck-reports/window", response_model=SuccessResponse[DynamicReportWindowResponse])
@inject
async def get_shopdeck_report_window(
    window_service: ShopDeckReportWindowService = Depends(Provide[DomainsContainer.operations.report_window_service])
):
    response = await window_service.calculate_required_window()
    return SuccessResponse(data=response)


class ReconciliationResponse(BaseModel):
    summary: ReconciliationSummary

@router.post("/shopdeck-reports/reconcile", response_model=SuccessResponse[ReconciliationResponse])
@inject
async def reconcile_shopdeck_report(
    file: UploadFile = File(...),
    uploaded_report_start_date: date = None,
    uploaded_report_end_date: date = None,
    orchestrator: ReconciliationOrchestratorService = Depends(Provide[DomainsContainer.operations.reconciliation_orchestrator])
):
    from src.foundation.exceptions.base import ValidationException
    if not uploaded_report_start_date or not uploaded_report_end_date:
        raise ValidationException(message="uploaded_report_start_date and uploaded_report_end_date are required.")

    content = await file.read()
    
    reader = ShopDeckOrderReader()
    validator = ShopDeckOrderValidator()
    mapper = ShopDeckOrderMapper()
    
    grouped_raw_list = reader.read(content)
    normalized_records = []
    
    for grouped_raw in grouped_raw_list:
        errors = validator.validate(grouped_raw)
        if not errors:
            normalized = mapper.map(grouped_raw)
            normalized_records.append(normalized)

    try:
        summary = await orchestrator.reconcile_report(
            normalized_records=normalized_records,
            uploaded_report_start_date=uploaded_report_start_date,
            uploaded_report_end_date=uploaded_report_end_date,
            source_reference=file.filename
        )
    except ValueError as e:
        raise ValidationException(message=str(e))
        
    return SuccessResponse(data=ReconciliationResponse(summary=summary))
