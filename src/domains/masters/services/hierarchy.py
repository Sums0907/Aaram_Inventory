from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.category_attribute import CategoryAttributeModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.schemas.hierarchy import HierarchyResponse
from src.foundation.enums import ItemType

class InventoryHierarchyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_hierarchy(self) -> dict:
        # Fetch all categories
        cat_result = await self.session.execute(
            select(CategoryModel)
            .options(selectinload(CategoryModel.category_attributes).selectinload(CategoryAttributeModel.attribute))
            .order_by(CategoryModel.category_name)
        )
        categories = cat_result.scalars().all()

        # Fetch all products (Master Items)
        prod_result = await self.session.execute(
            select(ProductModel).options(selectinload(ProductModel.skus)).order_by(ProductModel.product_name)
        )
        products = prod_result.scalars().all()
        
        # We return the flat lists and let the frontend build the VS Code style explorer tree
        # This keeps the payload small and simple.
        return {
            "categories": categories,
            "products": products
        }
