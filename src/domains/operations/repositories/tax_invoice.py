from uuid import UUID
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.operations.models.tax_invoice import TaxInvoiceModel, TaxInvoiceItemModel
from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.schemas.tax_invoice import TaxInvoiceCreate


class TaxInvoiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_invoice(self, data: TaxInvoiceCreate, created_by: UUID) -> TaxInvoiceModel:
        invoice_dict = data.model_dump(exclude={"items"})
        invoice_dict["created_by"] = created_by
        invoice_dict["updated_by"] = created_by
        
        db_invoice = TaxInvoiceModel(**invoice_dict)
        
        for item_data in data.items:
            item_dict = item_data.model_dump()
            item_dict["created_by"] = created_by
            item_dict["updated_by"] = created_by
            db_item = TaxInvoiceItemModel(**item_dict)
            db_invoice.items.append(db_item)
            
        self.session.add(db_invoice)
        await self.session.commit()
        await self.session.refresh(db_invoice)
        return db_invoice
        
    async def get_by_invoice_no(self, invoice_no: str) -> TaxInvoiceModel | None:
        stmt = select(TaxInvoiceModel).where(TaxInvoiceModel.invoice_no == invoice_no)
        result = await self.session.execute(stmt)
        return result.scalars().first()
