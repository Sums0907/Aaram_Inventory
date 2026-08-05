from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.foundation.api.responses import SuccessResponse
from src.app.services.business_summary import BusinessSummaryService

from src.app.container import DomainsContainer

router = APIRouter(tags=["Dashboard"])

@router.get("/summary", response_model=SuccessResponse[dict])
@inject
async def get_dashboard_summary(
    current_user: CurrentUser = Depends(get_current_user),
    summary_service: BusinessSummaryService = Depends(Provide[DomainsContainer.business_summary_service])
):
    """
    Returns the Business Summary containing aggregate operational and accounting statistics.
    """
    summary = await summary_service.get_summary()
    return SuccessResponse(data=summary)
