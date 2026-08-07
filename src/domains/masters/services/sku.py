from typing import List
from uuid import UUID
from src.domains.masters.repositories.sku import SKURepository
from src.domains.masters.repositories.product import ProductRepository
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.schemas.sku import SKUCreate, SKUUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException
from src.foundation.enums.status import GenericStatus

class SKUService:
    def __init__(self, repository: SKURepository, product_repo: ProductRepository):
        self.repository = repository
        self.product_repo = product_repo

    async def get_sku(self, sku_id: UUID) -> SKUModel:
        sku = await self.repository.get_by_id(sku_id)
        if not sku:
            raise NotFoundException(message="SKU not found")
        return sku
        
    async def list_skus(self, skip: int = 0, limit: int = 100) -> List[SKUModel]:
        return await self.repository.get_all(skip=skip, limit=limit)
        
    async def _validate_uniqueness(self, schema, sku_id: UUID = None):
        pass

    async def create_sku(self, schema: SKUCreate, created_by: UUID) -> SKUModel:
        if await self.repository.get_by_code(schema.sku_code):
            raise ValidationException(message="SKU Code must be unique")
            
        if schema.barcode and await self.repository.get_by_barcode(schema.barcode):
            raise ValidationException(message="Barcode must be unique")
            
        product = await self.product_repo.get_by_id(schema.product_id)
        if not product or product.status != GenericStatus.ACTIVE:
            raise ValidationException(message="Valid and Active Product is required")
            
        existing_attrs = await self.repository.get_by_product_and_attributes(schema.product_id, schema.attribute_values)
        if existing_attrs:
            raise ValidationException(message="Attribute combination must be unique within a Product")

        sku = SKUModel(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(sku)

    async def update_sku(self, sku_id: UUID, schema: SKUUpdate, updated_by: UUID) -> SKUModel:
        sku = await self.get_sku(sku_id)
        
        if schema.barcode and schema.barcode != sku.barcode:
            if await self.repository.get_by_barcode(schema.barcode):
                raise ValidationException(message="Barcode must be unique")
                
        existing_attrs = await self.repository.get_by_product_and_attributes(sku.product_id, schema.attribute_values)
        if existing_attrs and existing_attrs.id != sku.id:
            raise ValidationException(message="Attribute combination must be unique within a Product")
            
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(sku, key, value)
            
        sku.updated_by = updated_by
        return await self.repository.update(sku)
        
    async def activate_sku(self, sku_id: UUID, updated_by: UUID) -> SKUModel:
        sku = await self.get_sku(sku_id)
        if sku.status == GenericStatus.ACTIVE:
            raise ValidationException(message="SKU is already active")
        sku.status = GenericStatus.ACTIVE
        sku.updated_by = updated_by
        return await self.repository.update(sku)

    async def deactivate_sku(self, sku_id: UUID, updated_by: UUID) -> SKUModel:
        sku = await self.get_sku(sku_id)
        if sku.status == GenericStatus.INACTIVE:
            raise ValidationException(message="SKU is already inactive")
        sku.status = GenericStatus.INACTIVE
        sku.updated_by = updated_by
        return await self.repository.update(sku)
        
    async def archive_sku(self, sku_id: UUID, updated_by: UUID) -> SKUModel:
        sku = await self.get_sku(sku_id)
        if sku.status == GenericStatus.ARCHIVED:
            raise ValidationException(message="SKU is already archived")
        sku.status = GenericStatus.ARCHIVED
        sku.updated_by = updated_by
        return await self.repository.update(sku)
