from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.masters.models.category import CategoryModel

class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, category_id: UUID) -> Optional[CategoryModel]:
        result = await self.session.execute(select(CategoryModel).filter(CategoryModel.id == category_id))
        return result.scalars().first()

    async def get_by_code(self, category_code: str) -> Optional[CategoryModel]:
        result = await self.session.execute(select(CategoryModel).filter(CategoryModel.category_code == category_code))
        return result.scalars().first()
        
    async def get_by_name(self, category_name: str) -> Optional[CategoryModel]:
        result = await self.session.execute(select(CategoryModel).filter(CategoryModel.category_name == category_name))
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[CategoryModel]:
        result = await self.session.execute(select(CategoryModel).order_by(CategoryModel.display_order.asc().nulls_last()).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, category: CategoryModel) -> CategoryModel:
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def update(self, category: CategoryModel) -> CategoryModel:
        await self.session.commit()
        await self.session.refresh(category)
        return category
