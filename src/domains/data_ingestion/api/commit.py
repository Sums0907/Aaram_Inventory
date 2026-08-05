from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from dependency_injector.wiring import inject, Provide
from src.foundation.api.responses import SuccessResponse
from src.foundation.authentication.dependencies import CurrentUser, get_current_user
from src.domains.data_ingestion.dependency_injection import DataIngestionContainer
from src.domains.data_ingestion.services.commit import CommitService

router = APIRouter(prefix="/import-jobs", tags=["Data Ingestion - Workflow"])

@router.post("/{job_id}/approve", response_model=SuccessResponse)
@inject
async def approve_import_job(
    job_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    commit_service: CommitService = Depends(Provide[DataIngestionContainer.commit_service])
):
    try:
        user_uuid = UUID(current_user.id)
        await commit_service.approve_job_records(job_id, user_uuid)
        return SuccessResponse(data={"message": f"Job {job_id} approved successfully."})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{job_id}/commit", response_model=SuccessResponse)
@inject
async def commit_import_job(
    job_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    commit_service: CommitService = Depends(Provide[DataIngestionContainer.commit_service])
):
    try:
        user_uuid = UUID(current_user.id)
        # Note: In a production setting, this could be sent to a BackgroundTask to prevent timeout
        await commit_service.commit_job_records(job_id, user_uuid)
        return SuccessResponse(data={"message": f"Job {job_id} committed successfully."})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
