from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional, List
from io import BytesIO
from datetime import datetime
import pandas as pd
from dependency_injector.wiring import inject, Provide

from src.domains.data_ingestion.dependency_injection import DataIngestionContainer
from src.domains.data_ingestion.services.master_data_application_service import MasterDataApplicationService
from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.domains.data_ingestion.models.import_audit_log import ImportAuditLogModel

master_data_router = APIRouter(prefix="/master-data", tags=["Master Data Operations"])

@master_data_router.post("/import")
@inject
async def import_master_data(
    domain: str = Form(...),
    is_dry_run: bool = Form(...),
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    app_service: MasterDataApplicationService = Depends(Provide[DataIngestionContainer.master_data_application_service])
):
    # Permission Enforcement: Only users with MASTER_DATA_IMPORT permission can import
    app_service.validate_permissions(current_user.permissions, ["MASTER_DATA_IMPORT"])

    # Pre-execution file validation
    if not file.filename.endswith(('.xlsx', '.csv')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .xlsx and .csv allowed.")

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10 MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    try:
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(file_bytes)).fillna("")
        else:
            df = pd.read_csv(BytesIO(file_bytes)).fillna("")
        data = df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if not data:
        raise HTTPException(status_code=400, detail="File is empty or missing expected columns.")

    result = await app_service.execute_import(
        domain=domain,
        data=data,
        is_dry_run=is_dry_run,
        user_id=current_user.id,
        file_name=file.filename,
        env="prod" # In a real system, this comes from settings
    )
    
    return result

@master_data_router.get("/export")
@inject
async def export_master_data(
    current_user: CurrentUser = Depends(get_current_user),
    app_service: MasterDataApplicationService = Depends(Provide[DataIngestionContainer.master_data_application_service])
):
    # Permission Enforcement:
    app_service.validate_permissions(current_user.permissions, ["MASTER_DATA_EXPORT"])
    
    # In a real system, domain might filter the export. The current exporter exports all.
    export_data = await app_service.execute_export()
    
    # Simple single sheet conversion for demonstration since exporter returns Dict[str, List[Dict]]
    # Typically, we write multiple sheets into an in-memory BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, records in export_data.items():
            df = pd.DataFrame(records)
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            
    output.seek(0)
    
    # Track export event in audit log (simplified via the application service in a full implementation)
    # For now, we return the file
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=master_data_export.xlsx"}
    )

@master_data_router.get("/activity-history")
@inject
async def get_activity_history(
    domain: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    app_service: MasterDataApplicationService = Depends(Provide[DataIngestionContainer.master_data_application_service])
):
    # Permission Enforcement:
    app_service.validate_permissions(current_user.permissions, ["MASTER_DATA_ACTIVITY_VIEW"])
    
    session = app_service.session
    from sqlalchemy import select
    
    query = select(ImportAuditLogModel)
    
    if domain:
        query = query.where(ImportAuditLogModel.entity_type == domain.upper())
    if status:
        query = query.where(ImportAuditLogModel.status == status.upper())
        
    query = query.order_by(ImportAuditLogModel.start_time.desc()).offset(skip).limit(limit)
    
    result = await session.execute(query)
    logs = result.scalars().all()
    
    return logs
