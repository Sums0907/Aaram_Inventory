from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.matching.models.exception import MatchExceptionModel

class MatchExceptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_open_exceptions(self, skip: int = 0, limit: int = 100) -> List[MatchExceptionModel]:
        result = await self.session.execute(
            select(MatchExceptionModel).filter(
                MatchExceptionModel.status == "OPEN"
            ).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create_batch(self, exceptions: List[MatchExceptionModel]) -> None:
        self.session.add_all(exceptions)
        await self.session.commit()

    async def update(self, exception: MatchExceptionModel) -> MatchExceptionModel:
        await self.session.commit()
        await self.session.refresh(exception)
        return exception
