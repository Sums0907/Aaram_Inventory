from uuid import UUID
from src.domains.masters.repositories.bom import BOMRepository
from src.domains.masters.schemas.bom import BOMCreate

class BOMService:
    def __init__(self, repository: BOMRepository):
        self.repository = repository
        
    async def create_bom(self, schema: BOMCreate, created_by: UUID):
        return await self.repository.create_bom(schema, created_by)

    async def get_bom(self, bom_id: UUID):
        return await self.repository.get_bom(bom_id)

    async def get_all(self):
        return await self.repository.get_all()

    async def archive_bom(self, bom_id: UUID) -> bool:
        return await self.repository.archive_bom(bom_id)

    async def restore_bom(self, bom_id: UUID) -> bool:
        return await self.repository.restore_bom(bom_id)
