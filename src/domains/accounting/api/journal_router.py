from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Callable, AsyncContextManager
from dependency_injector.wiring import Provide, inject

from src.foundation.api.responses import SuccessResponse
from src.domains.accounting.models.journal import JournalEntryModel, JournalLineModel
from src.domains.accounting.models.ledger import LedgerModel
from src.app.container import DomainsContainer

router = APIRouter(tags=["accounting"])

@router.get("/journals", response_model=SuccessResponse[List[Dict[str, Any]]])
@inject
async def list_journals(
    limit: int = Query(50, ge=1, le=100),
    session_factory: Callable[..., AsyncContextManager[AsyncSession]] = Depends(Provide[DomainsContainer.core.db.provided._session_factory])
):
    async with session_factory() as session:
        stmt = select(JournalEntryModel).order_by(JournalEntryModel.journal_date.desc()).limit(limit)
        result = await session.execute(stmt)
        entries = result.scalars().all()
        
        response_data = []
        for entry in entries:
            # Fetch lines for each entry
            lines_stmt = select(JournalLineModel, LedgerModel.ledger_name).join(
                LedgerModel, LedgerModel.id == JournalLineModel.ledger_id
            ).where(JournalLineModel.journal_id == entry.id)
            
            lines_result = await session.execute(lines_stmt)
            lines = lines_result.all()
            
            formatted_lines = []
            for line, ledger_name in lines:
                formatted_lines.append({
                    "ledger_name": ledger_name,
                    "debit_amount": float(line.debit_amount),
                    "credit_amount": float(line.credit_amount),
                    "narration": line.narration
                })
                
            response_data.append({
                "journal_number": entry.journal_number,
                "journal_date": entry.journal_date,
                "posting_date": entry.posting_date,
                "reference_type": entry.reference_type,
                "reference_number": entry.reference_number,
                "status": entry.status,
                "lines": formatted_lines
            })
            
        return SuccessResponse(data=response_data)
