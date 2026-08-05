from uuid import UUID
from src.domains.operations.schemas.settlement import SettlementCreate
from src.domains.operations.repositories.settlement import SettlementRepository
from src.domains.operations.models.settlement import SettlementModel
from src.foundation.exceptions.base import AlreadyExistsException

class SettlementService:
    def __init__(self, repository: SettlementRepository):
        self.repository = repository
        
    async def process_commit(self, data: SettlementCreate, committed_by: UUID) -> SettlementModel:
        existing = await self.repository.get_by_settlement_id(data.settlement_id)
        if existing:
            raise AlreadyExistsException(
                message=f"Settlement with ID {data.settlement_id} already exists."
            )
            
        return await self.repository.create_settlement(data, committed_by)
