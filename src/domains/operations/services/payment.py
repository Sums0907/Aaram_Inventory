from uuid import UUID
from src.domains.operations.schemas.payment import PaymentCreate
from src.domains.operations.repositories.payment import PaymentRepository
from src.domains.operations.models.payment import PaymentModel
from src.foundation.exceptions.base import AlreadyExistsException

class PaymentService:
    def __init__(self, repository: PaymentRepository):
        self.repository = repository
        
    async def process_commit(self, data: PaymentCreate, committed_by: UUID) -> PaymentModel:
        existing = await self.repository.get_by_transaction_id(data.transaction_id)
        if existing:
            raise AlreadyExistsException(
                message=f"Payment with transaction ID {data.transaction_id} already exists."
            )
            
        return await self.repository.create_payment(data, committed_by)
