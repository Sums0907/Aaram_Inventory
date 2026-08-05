from uuid import UUID
from src.domains.operations.schemas.sales_order import SalesOrderCreate
from src.domains.operations.repositories.sales_order import SalesOrderRepository
from src.domains.operations.models.sales_order import SalesOrderModel
from src.foundation.exceptions.base import AlreadyExistsException

class SalesOrderService:
    def __init__(self, repository: SalesOrderRepository):
        self.repository = repository
        
    async def process_commit(self, data: SalesOrderCreate, committed_by: UUID) -> SalesOrderModel:
        # Check if already exists to prevent duplicate commits
        existing = await self.repository.get_by_external_id(data.external_order_id)
        if existing:
            # For V1, if it exists, we skip or raise. We'll raise to bubble up the duplicate issue.
            raise AlreadyExistsException(
                message=f"Sales Order with external ID {data.external_order_id} already exists."
            )
            
        return await self.repository.create_order(data, committed_by)
