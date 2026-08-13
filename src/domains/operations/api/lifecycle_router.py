from fastapi import APIRouter, Depends, UploadFile, File
from datetime import date
from typing import Optional
from pydantic import BaseModel
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse
from src.domains.operations.dependency_injection import OperationsContainer
from src.domains.operations.services.reconciliation_orchestrator import ReconciliationOrchestratorService, ReconciliationSummary
from src.domains.data_ingestion.services.adapters.shopdeck_order import ShopDeckOrderReader, ShopDeckOrderValidator, ShopDeckOrderMapper

router = APIRouter(prefix="/lifecycle", tags=["Operations - Lifecycle"])

class ReconciliationResponse(BaseModel):
    summary: ReconciliationSummary

@router.post("/shopdeck-reports/reconcile", response_model=SuccessResponse[ReconciliationResponse])
@inject
async def reconcile_shopdeck_report(
    file: UploadFile = File(...),
    uploaded_report_start_date: date = None,
    uploaded_report_end_date: date = None,
    orchestrator: ReconciliationOrchestratorService = Depends(Provide[OperationsContainer.reconciliation_orchestrator])
):
    from src.foundation.exceptions.base import BadRequestException
    if not uploaded_report_start_date or not uploaded_report_end_date:
        raise BadRequestException(message="uploaded_report_start_date and uploaded_report_end_date are required.")

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
        raise BadRequestException(message=str(e))
        
    return SuccessResponse(data=ReconciliationResponse(summary=summary))
