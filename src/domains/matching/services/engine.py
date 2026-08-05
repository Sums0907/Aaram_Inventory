from uuid import UUID
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.domains.matching.models.job import MatchJobModel
from src.domains.matching.models.relationship import MatchRelationshipModel
from src.domains.matching.models.exception import MatchExceptionModel
from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.models.tax_invoice import TaxInvoiceModel
from src.domains.operations.models.payment import PaymentModel
from src.domains.operations.models.settlement import SettlementModel

class MatchingEngineService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def run_matching_job(self, job_id: UUID) -> MatchJobModel:
        # Create a new job if none exists, but wait, the job is passed in.
        stmt = select(MatchJobModel).where(MatchJobModel.id == job_id)
        result = await self.session.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            job = MatchJobModel(id=job_id, started_on=datetime.now(timezone.utc), status="RUNNING")
            self.session.add(job)
            await self.session.commit()
            
        await self._match_sales_orders_and_invoices(job)
        await self._match_payments_and_settlements(job)
        
        job.status = "COMPLETED"
        job.completed_on = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(job)
        
        return job

    async def _match_sales_orders_and_invoices(self, job: MatchJobModel):
        # Find unmatched TaxInvoices
        stmt = select(TaxInvoiceModel).where(TaxInvoiceModel.order_id.is_(None))
        result = await self.session.execute(stmt)
        unmatched_invoices = result.scalars().all()
        
        for invoice in unmatched_invoices:
            job.invoices_processed += 1
            
            # Find matching order
            order_stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == invoice.external_order_id)
            order_result = await self.session.execute(order_stmt)
            order = order_result.scalars().first()
            
            if order:
                # Create relationship
                rel = MatchRelationshipModel(
                    match_job_id=job.id,
                    source_type="TAX_INVOICE",
                    source_id=invoice.id,
                    target_type="SALES_ORDER",
                    target_id=order.id,
                    relationship_type="INVOICE_TO_ORDER"
                )
                self.session.add(rel)
                
                # Update Operations Document
                invoice.order_id = order.id
                
                job.successful_matches += 1
            else:
                # Create Exception
                exc = MatchExceptionModel(
                    match_job_id=job.id,
                    document_type="TAX_INVOICE",
                    document_id=invoice.id,
                    reason=f"No SalesOrder found for external_order_id: {invoice.external_order_id}"
                )
                self.session.add(exc)
                job.exceptions_generated += 1
                job.failed_matches += 1

        await self.session.commit()

    async def _match_payments_and_settlements(self, job: MatchJobModel):
        # Find unmatched Payments that have an external_settlement_id
        stmt = select(PaymentModel).where(
            PaymentModel.settlement_id.is_(None),
            PaymentModel.external_settlement_id.is_not(None)
        )
        result = await self.session.execute(stmt)
        unmatched_payments = result.scalars().all()
        
        for payment in unmatched_payments:
            job.payments_processed += 1
            
            # Find matching settlement
            settlement_stmt = select(SettlementModel).where(SettlementModel.settlement_id == payment.external_settlement_id)
            settlement_result = await self.session.execute(settlement_stmt)
            settlement = settlement_result.scalars().first()
            
            if settlement:
                # Create relationship
                rel = MatchRelationshipModel(
                    match_job_id=job.id,
                    source_type="PAYMENT",
                    source_id=payment.id,
                    target_type="SETTLEMENT",
                    target_id=settlement.id,
                    relationship_type="PAYMENT_TO_SETTLEMENT"
                )
                self.session.add(rel)
                
                # Update Operations Document
                payment.settlement_id = settlement.id
                
                job.successful_matches += 1
            else:
                # Create Exception
                exc = MatchExceptionModel(
                    match_job_id=job.id,
                    document_type="PAYMENT",
                    document_id=payment.id,
                    reason=f"No Settlement found for external_settlement_id: {payment.external_settlement_id}"
                )
                self.session.add(exc)
                job.exceptions_generated += 1
                job.failed_matches += 1

        await self.session.commit()
