from typing import List
from uuid import UUID
from src.domains.masters.repositories.product import ProductRepository
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.models.product import ProductModel
from src.domains.masters.schemas.product import ProductCreate, ProductUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException
from src.foundation.enums.status import GenericStatus

class ProductService:
    def __init__(self, 
                 repository: ProductRepository,
                 category_repo: CategoryRepository):
        self.repository = repository
        self.category_repo = category_repo

    async def get_product(self, product_id: UUID) -> ProductModel:
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise NotFoundException(message="Product not found")
        return product
        
    async def list_products(self, skip: int = 0, limit: int = 100) -> List[ProductModel]:
        return await self.repository.get_all(skip=skip, limit=limit)
        
    async def _validate_references(self, category_id: UUID):
        if category_id:
            category = await self.category_repo.get_by_id(category_id)
            if not category or category.status != GenericStatus.ACTIVE:
                raise ValidationException(message="Valid and Active Category is required")
        
    async def create_product(self, schema: ProductCreate, created_by: UUID) -> ProductModel:
        if await self.repository.get_by_code(schema.product_code):
            raise ValidationException(message="Product Code must be unique")
            
        await self._validate_references(schema.category_id)
        
        attributes = await self.repository.get_product_attributes_by_ids(schema.product_attribute_ids or [])
        if len(attributes) != len(schema.product_attribute_ids or []):
            raise ValidationException(message="One or more Product Attributes are invalid")
            
        # Ensure only Active attributes are assigned
        for attr in attributes:
            if attr.status != GenericStatus.ACTIVE:
                raise ValidationException(message=f"Product Attribute {attr.attribute_name} is not active")

        model_data = schema.model_dump(exclude={"product_attribute_ids"})
        product = ProductModel(
            **model_data,
            attributes=attributes,
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(product)

    async def update_product(self, product_id: UUID, schema: ProductUpdate, updated_by: UUID) -> ProductModel:
        product = await self.get_product(product_id)
        
        await self._validate_references(schema.category_id)
        
        attributes = await self.repository.get_product_attributes_by_ids(schema.product_attribute_ids or [])
        if len(attributes) != len(schema.product_attribute_ids or []):
            raise ValidationException(message="One or more Product Attributes are invalid")
            
        update_data = schema.model_dump(exclude_unset=True, exclude={"product_attribute_ids"})
        for key, value in update_data.items():
            setattr(product, key, value)
            
        product.attributes = attributes
        product.updated_by = updated_by
        return await self.repository.update(product)
        
    async def activate_product(self, product_id: UUID, updated_by: UUID) -> ProductModel:
        product = await self.get_product(product_id)
        if product.status == GenericStatus.ACTIVE:
            raise ValidationException(message="Product is already active")
        product.status = GenericStatus.ACTIVE
        product.updated_by = updated_by
        return await self.repository.update(product)

    async def deactivate_product(self, product_id: UUID, updated_by: UUID) -> ProductModel:
        product = await self.get_product(product_id)
        if product.status == GenericStatus.INACTIVE:
            raise ValidationException(message="Product is already inactive")
        product.status = GenericStatus.INACTIVE
        product.updated_by = updated_by
        return await self.repository.update(product)
        
    async def archive_product(self, product_id: UUID, updated_by: UUID) -> ProductModel:
        product = await self.get_product(product_id)
        if product.status == GenericStatus.ARCHIVED:
            raise ValidationException(message="Product is already archived")
        product.status = GenericStatus.ARCHIVED
        product.updated_by = updated_by
        return await self.repository.update(product)
