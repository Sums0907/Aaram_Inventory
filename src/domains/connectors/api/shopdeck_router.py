import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.domains.connectors.container import ConnectorsContainer

router = APIRouter(tags=["ShopDeck Connector"])

from pydantic import BaseModel
from typing import Optional
from datetime import date

class SyncRequest(BaseModel):
    integration_id: str
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    report_type: Optional[str] = None

@router.post("/sync", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def sync_shopdeck(
    request: SyncRequest,
    current_user: CurrentUser = Depends(get_current_user),
    shopdeck_sync_service = Depends(Provide[ConnectorsContainer.shopdeck_sync_service])
):
    """
    Triggers a synchronization event for ShopDeck.
    """
    result = await shopdeck_sync_service.run_sync(
        user_id=uuid.UUID(current_user.id),
        period_start=request.period_start,
        period_end=request.period_end,
        report_type=request.report_type
    )
    return SuccessResponse(data=result)

@router.get("/status", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def get_shopdeck_status(
    current_user: CurrentUser = Depends(get_current_user)
):
    return SuccessResponse(data={"status": "CONNECTED"})

@router.get("/history", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def get_shopdeck_history(
    current_user: CurrentUser = Depends(get_current_user)
):
    return SuccessResponse(data={"history": []})

@router.get("/reports", response_model=SuccessResponse[Dict[str, Any]])
@inject
async def get_shopdeck_reports(
    current_user: CurrentUser = Depends(get_current_user)
):
    return SuccessResponse(data={"reports": []})

from fastapi.responses import FileResponse
import os
from src.foundation.configuration.settings import get_settings
from dependency_injector.wiring import inject, Provide
from src.domains.connectors.container import ConnectorsContainer
from src.domains.connectors.services.storage import StorageManager

@router.get("/reports/{filename}/download")
@inject
async def download_shopdeck_report(
    filename: str,
    current_user: CurrentUser = Depends(get_current_user),
    storage_manager: StorageManager = Depends(Provide[ConnectorsContainer.storage_manager])
):
    storage_dir = os.path.join(storage_manager.base_storage_dir, "shopdeck")
    if not os.path.exists(storage_dir):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Storage not found")
        
    name, ext = os.path.splitext(filename)
    
    # Recursively find the most recent file that starts with `name`
    latest_file = None
    latest_mtime = 0
    
    for root, _, files in os.walk(storage_dir):
        for f in files:
            if f.startswith(name) and f.endswith(ext):
                full_path = os.path.join(root, f)
                mtime = os.path.getmtime(full_path)
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest_file = full_path
                    
    if not latest_file:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(path=latest_file, filename=filename, media_type='text/csv')
