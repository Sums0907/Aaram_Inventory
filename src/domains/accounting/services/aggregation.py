from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import defaultdict
import pandas as pd
from decimal import Decimal

from src.domains.accounting.models.journal import JournalEntryModel, JournalLineModel
from src.domains.accounting.models.ledger import LedgerModel
from src.domains.operations.models.tax_invoice import TaxInvoiceModel

class JournalAggregationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def aggregate_sales_journal(self) -> pd.DataFrame:
        stmt = (
            select(JournalLineModel.debit_amount, JournalLineModel.credit_amount, LedgerModel.ledger_name)
            .join(JournalEntryModel, JournalLineModel.journal_id == JournalEntryModel.id)
            .join(LedgerModel, JournalLineModel.ledger_id == LedgerModel.id)
            .join(TaxInvoiceModel, JournalEntryModel.reference_id == TaxInvoiceModel.id)
            .where(JournalEntryModel.reference_type == "TAX_INVOICE")
            .where(TaxInvoiceModel.document_type.ilike("%INVOICE%"))
        )
        return await self._build_journal_df(stmt)

    async def aggregate_credit_note_journal(self) -> pd.DataFrame:
        stmt = (
            select(JournalLineModel.debit_amount, JournalLineModel.credit_amount, LedgerModel.ledger_name)
            .join(JournalEntryModel, JournalLineModel.journal_id == JournalEntryModel.id)
            .join(LedgerModel, JournalLineModel.ledger_id == LedgerModel.id)
            .join(TaxInvoiceModel, JournalEntryModel.reference_id == TaxInvoiceModel.id)
            .where(JournalEntryModel.reference_type == "TAX_INVOICE")
            .where(TaxInvoiceModel.document_type.ilike("%CREDIT%"))
        )
        return await self._build_journal_df(stmt)

    async def aggregate_settlement_journal(self) -> pd.DataFrame:
        # Settlements are reference_type == "PAYMENT"
        stmt = (
            select(JournalLineModel.debit_amount, JournalLineModel.credit_amount, LedgerModel.ledger_name)
            .join(JournalEntryModel, JournalLineModel.journal_id == JournalEntryModel.id)
            .join(LedgerModel, JournalLineModel.ledger_id == LedgerModel.id)
            .where(JournalEntryModel.reference_type == "PAYMENT")
        )
        return await self._build_journal_df(stmt, is_settlement=True)

    async def _build_journal_df(self, stmt, is_settlement=False) -> pd.DataFrame:
        result = await self.session.execute(stmt)
        rows = result.all()
        
        totals = defaultdict(lambda: {"debit": Decimal("0"), "credit": Decimal("0")})
        
        for debit, credit, ledger_name in rows:
            totals[ledger_name]["debit"] += Decimal(str(debit))
            totals[ledger_name]["credit"] += Decimal(str(credit))
            
        journal_rows = []
        for ledger, amounts in totals.items():
            net = amounts["debit"] - amounts["credit"]
            if net > 0:
                journal_rows.append({"Ledger": ledger, "Debit": float(net), "Credit": 0.0})
            elif net < 0:
                journal_rows.append({"Ledger": ledger, "Debit": 0.0, "Credit": float(abs(net))})
                
        # Re-balance Round Off
        total_debit = Decimal(str(sum(r["Debit"] for r in journal_rows)))
        total_credit = Decimal(str(sum(r["Credit"] for r in journal_rows)))
        difference = total_debit - total_credit
        
        # Only add round off if there is a difference that is valid
        # For settlements, limit is 0.05
        if difference != 0:
            if is_settlement and abs(difference) > Decimal("0.05"):
                print(f"WARNING: Settlement Difference {difference} exceeds 0.05 limit")
                
            if difference > 0:
                journal_rows.append({"Ledger": "Round Off", "Debit": 0.0, "Credit": float(difference)})
            else:
                journal_rows.append({"Ledger": "Round Off", "Debit": float(abs(difference)), "Credit": 0.0})
                
        return pd.DataFrame(journal_rows)
