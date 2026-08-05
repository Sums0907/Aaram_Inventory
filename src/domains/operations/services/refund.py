from uuid import UUID
from src.domains.operations.schemas.refund import RefundCreate
from src.domains.operations.repositories.refund import RefundRepository
from src.domains.operations.models.refund import RefundModel
from src.foundation.exceptions.base import AlreadyExistsException

class RefundService:
    def __init__(self, repository: RefundRepository):
        self.repository = repository
        
    async def process_commit(self, data: RefundCreate, committed_by: UUID) -> RefundModel:
        existing = await self.repository.get_by_transaction_id(data.transaction_id)
        if existing:
            raise AlreadyExistsException(
                message=f"Refund with transaction ID {data.transaction_id} already exists."
            )
            
        return await self.repository.create_refund(data, committed_by)
