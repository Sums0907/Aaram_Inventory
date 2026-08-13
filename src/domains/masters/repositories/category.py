from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.category_attribute import CategoryAttributeModel

class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, category_id: UUID) -> Optional[CategoryModel]:
        result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.category_attributes).selectinload(CategoryAttributeModel.attribute))
            .filter(CategoryModel.id == category_id)
        )
        return result.scalars().first()

    async def get_by_code(self, category_code: str) -> Optional[CategoryModel]:
        result = await self.session.execute(select(CategoryModel).filter(CategoryModel.category_code == category_code))
        return result.scalars().first()
        
    async def get_by_name(self, category_name: str) -> Optional[CategoryModel]:
        result = await self.session.execute(select(CategoryModel).filter(CategoryModel.category_name == category_name))
        return result.scalars().first()
        
    async def get_all(self, skip: int = 0, limit: int = 100, item_type: Optional[str] = None) -> List[CategoryModel]:
        query = select(CategoryModel).options(
            selectinload(CategoryModel.category_attributes).selectinload(CategoryAttributeModel.attribute)
        )
        if item_type:
            query = query.filter(CategoryModel.item_type == item_type)
        result = await self.session.execute(query.order_by(CategoryModel.display_order.asc().nulls_last()).offset(skip).limit(limit))
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
        
    async def delete(self, category_id: UUID) -> None:
        category = await self.get_by_id(category_id)
        if category:
            await self.session.delete(category)
            await self.session.commit()

    async def set_category_attributes(self, category_id: UUID, attribute_names: List[str]) -> None:
        from src.domains.masters.models.product_attribute import ProductAttributeModel
        from src.domains.masters.models.category_attribute import CategoryAttributeModel
        import uuid

        # Fetch existing attributes
        result = await self.session.execute(
            select(ProductAttributeModel).filter(ProductAttributeModel.attribute_name.in_(attribute_names))
        )
        existing_attrs = {attr.attribute_name: attr for attr in result.scalars().all()}

        # Create missing attributes
        new_attrs = []
        for name in attribute_names:
            if name not in existing_attrs:
                code = f"ATTR-{uuid.uuid4().hex[:6].upper()}"
                new_attr = ProductAttributeModel(
                    attribute_code=code,
                    attribute_name=name
                )
                self.session.add(new_attr)
                new_attrs.append(new_attr)
                existing_attrs[name] = new_attr

        if new_attrs:
            await self.session.flush()

        # Delete old associations
        from sqlalchemy import delete
        await self.session.execute(
            delete(CategoryAttributeModel).filter(CategoryAttributeModel.category_id == category_id)
        )

        # Create new associations
        for name in attribute_names:
            attr = existing_attrs[name]
            assoc = CategoryAttributeModel(
                category_id=category_id,
                attribute_id=attr.id,
                is_required=True  # Defaulting all mapped attributes to required for now
            )
            self.session.add(assoc)
        
        await self.session.commit()
