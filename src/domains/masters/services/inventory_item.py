import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domains.masters.schemas.inventory_item import InventoryItemCreate
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.foundation.exceptions.base import ValidationException

class InventoryItemService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_or_create_category(self, schema: InventoryItemCreate, user_id: uuid.UUID) -> Optional[uuid.UUID]:
        if schema.category_id:
            return schema.category_id
        if schema.new_category_name:
            # Check if exists
            result = await self.session.execute(
                select(CategoryModel).filter(CategoryModel.category_name == schema.new_category_name)
            )
            cat = result.scalars().first()
            if cat:
                return cat.id
            
            # Generate code (e.g. CAT-RAW-001)
            cat = CategoryModel(
                category_code=f"CAT-{uuid.uuid4().hex[:6].upper()}",
                category_name=schema.new_category_name,
                item_type=schema.item_type,
                created_by=user_id,
                updated_by=user_id
            )
            self.session.add(cat)
            await self.session.flush()
            return cat.id
        return None

    async def _get_or_create_product(self, schema: InventoryItemCreate, category_id: Optional[uuid.UUID], user_id: uuid.UUID) -> uuid.UUID:
        if schema.product_id:
            return schema.product_id
        if schema.new_product_name:
            # Create product
            prod = ProductModel(
                product_code=f"PRD-{uuid.uuid4().hex[:6].upper()}",
                product_name=schema.new_product_name,
                item_type=schema.item_type,
                category_id=category_id,
                created_by=user_id,
                updated_by=user_id
            )
            self.session.add(prod)
            await self.session.flush()
            return prod.id
        
        raise ValidationException("Must provide product_id or new_product_name")

    async def create_inventory_item(self, schema: InventoryItemCreate, user_id: uuid.UUID) -> SKUModel:
        async with self.session.begin_nested():
            # 1. Resolve Category
            category_id = await self._get_or_create_category(schema, user_id)
            
            # 2. Resolve Master Item (Product)
            product_id = await self._get_or_create_product(schema, category_id, user_id)
            
            # 3. Ensure Item Code uniqueness
            result = await self.session.execute(
                select(SKUModel).filter(SKUModel.item_code == schema.item_code)
            )
            if result.scalars().first():
                raise ValidationException(f"Item Code {schema.item_code} is already in use.")

            # 4. Ensure SKU Code uniqueness (if provided)
            if schema.sku_code:
                result = await self.session.execute(
                    select(SKUModel).filter(SKUModel.sku_code == schema.sku_code)
                )
                if result.scalars().first():
                    raise ValidationException(f"SKU Code {schema.sku_code} is already in use.")
            
            # 5. Create Variant (SKU)
            barcode = schema.barcode if schema.barcode else None
            sku_code = schema.sku_code if schema.sku_code else None

            sku = SKUModel(
                item_code=schema.item_code,
                sku_code=sku_code,
                product_id=product_id,
                size=schema.size,
                color=schema.color,
                pattern=schema.pattern,
                material=schema.material,
                thread_count=schema.thread_count,
                attribute_values=schema.attribute_values,
                barcode=schema.barcode,
                created_by=user_id,
                updated_by=user_id
            )
            self.session.add(sku)
            await self.session.flush()
            
            return sku
