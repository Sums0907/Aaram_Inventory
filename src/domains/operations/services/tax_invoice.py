from uuid import UUID
from src.domains.operations.schemas.tax_invoice import TaxInvoiceCreate
from src.domains.operations.repositories.tax_invoice import TaxInvoiceRepository
from src.domains.operations.models.tax_invoice import TaxInvoiceModel
from src.foundation.exceptions.base import AlreadyExistsException

class TaxInvoiceService:
    def __init__(self, repository: TaxInvoiceRepository):
        self.repository = repository
        
    async def process_commit(self, data: TaxInvoiceCreate, committed_by: UUID) -> TaxInvoiceModel:
        existing = await self.repository.get_by_invoice_no(data.invoice_no)
        if existing:
            raise AlreadyExistsException(
                message=f"Tax Invoice {data.invoice_number} already exists."
            )
            
        return await self.repository.create_invoice(data, committed_by)
