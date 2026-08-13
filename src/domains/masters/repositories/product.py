from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.product_attribute import ProductAttributeModel

class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: UUID) -> Optional[ProductModel]:
        result = await self.session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.attributes))
            .filter(ProductModel.id == product_id)
        )
        return result.scalars().first()

    async def get_by_code(self, product_code: str) -> Optional[ProductModel]:
        result = await self.session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.attributes))
            .filter(ProductModel.product_code == product_code)
        )
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ProductModel]:
        result = await self.session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.attributes))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_product_attributes_by_ids(self, attribute_ids: List[UUID]) -> List[ProductAttributeModel]:
        if not attribute_ids:
            return []
        result = await self.session.execute(
            select(ProductAttributeModel).filter(ProductAttributeModel.id.in_(attribute_ids))
        )
        return list(result.scalars().all())

    async def create(self, product: ProductModel) -> ProductModel:
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update(self, product: ProductModel) -> ProductModel:
        await self.session.commit()
        await self.session.refresh(product)
        return product
        
    async def delete(self, product_id: UUID) -> None:
        product = await self.get_by_id(product_id)
        if product:
            await self.session.delete(product)
            await self.session.commit()
