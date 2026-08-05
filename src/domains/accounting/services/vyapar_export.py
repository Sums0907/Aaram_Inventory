import csv
from io import StringIO
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.domains.accounting.models.journal import JournalEntryModel

class VyaparExportService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def export_journals_to_csv(self) -> str:
        stmt = select(JournalEntryModel).options(selectinload(JournalEntryModel.lines))
        result = await self.session.execute(stmt)
        journals = result.scalars().all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers for a minimal Vyapar-like import format
        writer.writerow(["Date", "Journal Number", "Reference", "Account", "Debit", "Credit", "Narration"])
        
        for journal in journals:
            for line in journal.lines:
                # We mock the account name here since we just have the ledger ID on the line.
                # In a real implementation, we'd join with LedgerModel to get the ledger_name.
                account_name = str(line.ledger_id)
                writer.writerow([
                    journal.journal_date.isoformat(),
                    journal.journal_number,
                    f"{journal.reference_type}-{journal.reference_number}",
                    account_name,
                    str(line.debit_amount),
                    str(line.credit_amount),
                    line.narration or journal.narration or ""
                ])
                
        return output.getvalue()
