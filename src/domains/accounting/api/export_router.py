from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from dependency_injector.wiring import Provide, inject

from src.foundation.authentication.dependencies import get_current_user, CurrentUser
from src.domains.accounting.services.vyapar_export import VyaparExportService

from src.app.container import DomainsContainer

router = APIRouter(tags=["Accounting Export"])

@router.get("/vyapar/sales", response_class=PlainTextResponse)
@inject
async def export_vyapar_sales(
    current_user: CurrentUser = Depends(get_current_user),
    vyapar_export_service: VyaparExportService = Depends(Provide[DomainsContainer.accounting.vyapar_export_service])
):
    csv_content = await vyapar_export_service.export_sales_journal()
    return PlainTextResponse(content=csv_content, media_type="text/csv")

@router.get("/vyapar/credit-notes", response_class=PlainTextResponse)
@inject
async def export_vyapar_credit_notes(
    current_user: CurrentUser = Depends(get_current_user),
    vyapar_export_service: VyaparExportService = Depends(Provide[DomainsContainer.accounting.vyapar_export_service])
):
    csv_content = await vyapar_export_service.export_credit_note_journal()
    return PlainTextResponse(content=csv_content, media_type="text/csv")

@router.get("/vyapar/settlements", response_class=PlainTextResponse)
@inject
async def export_vyapar_settlements(
    current_user: CurrentUser = Depends(get_current_user),
    vyapar_export_service: VyaparExportService = Depends(Provide[DomainsContainer.accounting.vyapar_export_service])
):
    csv_content = await vyapar_export_service.export_settlement_journal()
    return PlainTextResponse(content=csv_content, media_type="text/csv")

from src.domains.accounting.services.aggregation import JournalAggregationService
from src.foundation.api.responses import SuccessResponse

@router.get("/json")
@inject
async def get_monthly_journals_json(
    current_user: CurrentUser = Depends(get_current_user),
    session_factory = Depends(Provide[DomainsContainer.core.db.provided._session_factory])
):
    async with session_factory() as session:
        aggregator = JournalAggregationService(session)
        sales_df = await aggregator.aggregate_sales_journal()
        credit_df = await aggregator.aggregate_credit_note_journal()
        settlement_df = await aggregator.aggregate_settlement_journal()
        
        return SuccessResponse(data={
            "sales": sales_df.to_dict(orient="records"),
            "credit_notes": credit_df.to_dict(orient="records"),
            "settlements": settlement_df.to_dict(orient="records")
        })
