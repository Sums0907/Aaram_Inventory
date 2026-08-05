from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.domains.data_ingestion.models.import_record import ImportRecordModel
from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.models.tax_invoice import TaxInvoiceModel
from src.domains.operations.models.payment import PaymentModel
from src.domains.operations.models.settlement import SettlementModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.accounting.models.journal import JournalEntryModel, JournalLineModel
from src.app.services.verification import VerificationService

class BusinessSummaryService:
    def __init__(self, session: AsyncSession, verification_service: VerificationService):
        self.session = session
        self.verification_service = verification_service
        
    async def get_summary(self) -> Dict[str, Any]:
        """
        Aggregates information across domains for business KPIs.
        """
        # Operations Counts
        sales_orders = await self._count(SalesOrderModel)
        tax_invoices = await self._count(TaxInvoiceModel)
        
        # Financial Aggregations
        revenue_stmt = select(func.sum(TaxInvoiceModel.total_base_price + TaxInvoiceModel.total_tax))
        revenue_result = await self.session.execute(revenue_stmt)
        total_revenue = revenue_result.scalar_one_or_none() or 0.0

        settlement_stmt = select(
            func.sum(SettlementModel.net_amount),
            func.sum(SettlementModel.fees)
        )
        settlement_result = await self.session.execute(settlement_stmt)
        settlement_data = settlement_result.first()
        total_settlements = settlement_data[0] if settlement_data and settlement_data[0] else 0.0
        total_fees = settlement_data[1] if settlement_data and settlement_data[1] else 0.0
        
        # Verification
        verification_result = await self.verification_service.verify_all()
        golden_dataset_status = verification_result["status"]
        
        return {
            "Total Revenue": float(total_revenue),
            "Total Settlements": float(total_settlements),
            "Platform Fees": float(total_fees),
            "Sales Orders": sales_orders,
            "Tax Invoices": tax_invoices,
            "Fulfillment Rate": round((tax_invoices / sales_orders * 100) if sales_orders > 0 else 0, 1),
            "Golden Dataset Status": golden_dataset_status
        }
        
    async def _count(self, model) -> int:
        stmt = select(func.count()).select_from(model)
        result = await self.session.execute(stmt)
        return result.scalar_one()
