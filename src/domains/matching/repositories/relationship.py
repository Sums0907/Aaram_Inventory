from uuid import UUID
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.matching.models.relationship import MatchRelationshipModel

class MatchRelationshipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_source(self, source_type: str, source_id: UUID) -> List[MatchRelationshipModel]:
        result = await self.session.execute(
            select(MatchRelationshipModel).filter(
                MatchRelationshipModel.source_type == source_type,
                MatchRelationshipModel.source_id == source_id
            )
        )
        return list(result.scalars().all())

    async def create_batch(self, relationships: List[MatchRelationshipModel]) -> None:
        self.session.add_all(relationships)
        await self.session.commit()
