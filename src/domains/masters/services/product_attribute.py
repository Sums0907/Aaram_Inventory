from typing import List
from uuid import UUID
from src.domains.masters.repositories.product_attribute import ProductAttributeRepository
from src.domains.masters.models.product_attribute import ProductAttributeModel
from src.domains.masters.schemas.product_attribute import ProductAttributeCreate, ProductAttributeUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException
from src.foundation.enums.status import GenericStatus

class ProductAttributeService:
    def __init__(self, repository: ProductAttributeRepository):
        self.repository = repository

    async def get_attribute(self, attribute_id: UUID) -> ProductAttributeModel:
        attribute = await self.repository.get_by_id(attribute_id)
        if not attribute:
            raise NotFoundException(message="Product Attribute not found")
        return attribute
        
    async def list_attributes(self, skip: int = 0, limit: int = 100) -> List[ProductAttributeModel]:
        return await self.repository.get_all(skip=skip, limit=limit)
        
    async def create_attribute(self, schema: ProductAttributeCreate, created_by: UUID) -> ProductAttributeModel:
        # Business Validation: Uniqueness
        if await self.repository.get_by_code(schema.attribute_code):
            raise ValidationException(message="Attribute Code must be unique")
        if await self.repository.get_by_name(schema.attribute_name):
            raise ValidationException(message="Attribute Name must be unique")
            
        attribute = ProductAttributeModel(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(attribute)

    async def update_attribute(self, attribute_id: UUID, schema: ProductAttributeUpdate, updated_by: UUID) -> ProductAttributeModel:
        attribute = await self.get_attribute(attribute_id)
        
        # Business Validation: Uniqueness (Exclude self)
        existing_name = await self.repository.get_by_name(schema.attribute_name)
        if existing_name and existing_name.id != attribute.id:
            raise ValidationException(message="Attribute Name must be unique")

        # Apply updates
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(attribute, key, value)
            
        attribute.updated_by = updated_by
        return await self.repository.update(attribute)
        
    async def activate_attribute(self, attribute_id: UUID, updated_by: UUID) -> ProductAttributeModel:
        attribute = await self.get_attribute(attribute_id)
        if attribute.status == GenericStatus.ACTIVE:
            raise ValidationException(message="Attribute is already active")
        attribute.status = GenericStatus.ACTIVE
        attribute.updated_by = updated_by
        return await self.repository.update(attribute)

    async def deactivate_attribute(self, attribute_id: UUID, updated_by: UUID) -> ProductAttributeModel:
        attribute = await self.get_attribute(attribute_id)
        if attribute.status == GenericStatus.INACTIVE:
            raise ValidationException(message="Attribute is already inactive")
        attribute.status = GenericStatus.INACTIVE
        attribute.updated_by = updated_by
        return await self.repository.update(attribute)
        
    async def archive_attribute(self, attribute_id: UUID, updated_by: UUID) -> ProductAttributeModel:
        attribute = await self.get_attribute(attribute_id)
        if attribute.status == GenericStatus.ARCHIVED:
            raise ValidationException(message="Attribute is already archived")
        attribute.status = GenericStatus.ARCHIVED
        attribute.updated_by = updated_by
        return await self.repository.update(attribute)
