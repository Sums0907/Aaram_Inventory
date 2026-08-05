from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.accounting.services.aggregation import JournalAggregationService

class VyaparExportService:
    def __init__(self, session: AsyncSession, aggregation_service: JournalAggregationService):
        self.session = session
        self.aggregation_service = aggregation_service
        
    async def export_sales_journal(self) -> str:
        df = await self.aggregation_service.aggregate_sales_journal()
        # Sort by Ledger alphabetically for deterministic output
        df = df.sort_values(by="Ledger")
        return df.to_csv(index=False)
        
    async def export_credit_note_journal(self) -> str:
        df = await self.aggregation_service.aggregate_credit_note_journal()
        df = df.sort_values(by="Ledger")
        return df.to_csv(index=False)
        
    async def export_settlement_journal(self) -> str:
        df = await self.aggregation_service.aggregate_settlement_journal()
        df = df.sort_values(by="Ledger")
        return df.to_csv(index=False)
