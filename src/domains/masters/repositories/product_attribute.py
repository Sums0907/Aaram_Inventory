from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.masters.models.product_attribute import ProductAttributeModel

class ProductAttributeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, attribute_id: UUID) -> Optional[ProductAttributeModel]:
        result = await self.session.execute(select(ProductAttributeModel).filter(ProductAttributeModel.id == attribute_id))
        return result.scalars().first()

    async def get_by_code(self, attribute_code: str) -> Optional[ProductAttributeModel]:
        result = await self.session.execute(select(ProductAttributeModel).filter(ProductAttributeModel.attribute_code == attribute_code))
        return result.scalars().first()
        
    async def get_by_name(self, attribute_name: str) -> Optional[ProductAttributeModel]:
        result = await self.session.execute(select(ProductAttributeModel).filter(ProductAttributeModel.attribute_name == attribute_name))
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ProductAttributeModel]:
        result = await self.session.execute(select(ProductAttributeModel).order_by(ProductAttributeModel.display_order.asc().nulls_last()).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, attribute: ProductAttributeModel) -> ProductAttributeModel:
        self.session.add(attribute)
        await self.session.commit()
        await self.session.refresh(attribute)
        return attribute

    async def update(self, attribute: ProductAttributeModel) -> ProductAttributeModel:
        await self.session.commit()
        await self.session.refresh(attribute)
        return attribute
