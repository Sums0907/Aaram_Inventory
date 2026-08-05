from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID, uuid4
from typing import List
from dependency_injector.wiring import Provide, inject

from src.domains.matching.schemas.job import MatchJobResponse
from src.domains.matching.schemas.exception import MatchExceptionResponse
from src.foundation.api.responses import SuccessResponse
from src.domains.matching.services.engine import MatchingEngineService
from src.domains.matching.repositories.exception import MatchExceptionRepository
from src.domains.matching.dependency_injection import MatchingContainer
from src.app.services.pipeline_orchestrator import PipelineOrchestratorService
from src.app.container import DomainsContainer

router = APIRouter(tags=["matching"])

@router.post("/jobs", response_model=SuccessResponse[MatchJobResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_matching_job(
    orchestrator_service: PipelineOrchestratorService = Depends(Provide[DomainsContainer.pipeline_orchestrator])
):
    job_id = uuid4()
    # Assume user_id is the default one for manual runs
    user_id = UUID("00000000-0000-0000-0000-000000000001")
    job = await orchestrator_service.run_pipeline(job_id, user_id)
    return SuccessResponse(data=MatchJobResponse.model_validate(job, from_attributes=True))

@router.get("/exceptions", response_model=SuccessResponse[List[MatchExceptionResponse]])
@inject
async def list_open_exceptions(
    skip: int = 0,
    limit: int = 100,
    exception_repo: MatchExceptionRepository = Depends(Provide[MatchingContainer.exception_repository])
):
    exceptions = await exception_repo.get_open_exceptions(skip=skip, limit=limit)
    response_data = [MatchExceptionResponse.model_validate(ex, from_attributes=True) for ex in exceptions]
    return SuccessResponse(data=response_data)
