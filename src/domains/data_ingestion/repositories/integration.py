from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.data_ingestion.models.integration import IntegrationModel

class IntegrationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, integration_id: UUID) -> Optional[IntegrationModel]:
        result = await self.session.execute(select(IntegrationModel).filter(IntegrationModel.id == integration_id))
        return result.scalars().first()

    async def get_by_code(self, code: str) -> Optional[IntegrationModel]:
        result = await self.session.execute(select(IntegrationModel).filter(IntegrationModel.integration_code == code))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[IntegrationModel]:
        result = await self.session.execute(select(IntegrationModel).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, integration: IntegrationModel) -> IntegrationModel:
        self.session.add(integration)
        await self.session.commit()
        await self.session.refresh(integration)
        return integration

    async def update(self, integration: IntegrationModel) -> IntegrationModel:
        await self.session.commit()
        await self.session.refresh(integration)
        return integration
