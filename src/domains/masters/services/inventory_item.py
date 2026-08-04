from typing import List
from uuid import UUID
from src.domains.masters.repositories.inventory_item import InventoryItemRepository
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository
from src.domains.masters.models.inventory_item import InventoryItemModel
from src.domains.masters.schemas.inventory_item import InventoryItemCreate, InventoryItemUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException
from src.foundation.enums.status import GenericStatus

class InventoryItemService:
    def __init__(self, 
                 repository: InventoryItemRepository,
                 category_repo: CategoryRepository,
                 uom_repo: UnitOfMeasureRepository):
        self.repository = repository
        self.category_repo = category_repo
        self.uom_repo = uom_repo

    async def get_item(self, item_id: UUID) -> InventoryItemModel:
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise NotFoundException(message="Inventory Item not found")
        return item
        
    async def list_items(self, skip: int = 0, limit: int = 100) -> List[InventoryItemModel]:
        return await self.repository.get_all(skip=skip, limit=limit)
        
    async def _validate_references(self, category_id: UUID, unit_of_measure_id: UUID):
        category = await self.category_repo.get_by_id(category_id)
        if not category or category.status != GenericStatus.ACTIVE:
            raise ValidationException(message="Valid and Active Category is required")
            
        uom = await self.uom_repo.get_by_id(unit_of_measure_id)
        if not uom or uom.status != GenericStatus.ACTIVE:
            raise ValidationException(message="Valid and Active Unit of Measure is required")
        
    async def create_item(self, schema: InventoryItemCreate, created_by: UUID) -> InventoryItemModel:
        if await self.repository.get_by_code(schema.item_code):
            raise ValidationException(message="Item Code must be unique")
            
        await self._validate_references(schema.category_id, schema.unit_of_measure_id)
        
        attributes = await self.repository.get_product_attributes_by_ids(schema.product_attribute_ids or [])
        if len(attributes) != len(schema.product_attribute_ids or []):
            raise ValidationException(message="One or more Product Attributes are invalid")
            
        # Ensure only Active attributes are assigned
        for attr in attributes:
            if attr.status != GenericStatus.ACTIVE:
                raise ValidationException(message=f"Product Attribute {attr.attribute_name} is not active")

        model_data = schema.model_dump(exclude={"product_attribute_ids"})
        item = InventoryItemModel(
            **model_data,
            product_attributes=attributes,
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(item)

    async def update_item(self, item_id: UUID, schema: InventoryItemUpdate, updated_by: UUID) -> InventoryItemModel:
        item = await self.get_item(item_id)
        
        await self._validate_references(schema.category_id, schema.unit_of_measure_id)
        
        attributes = await self.repository.get_product_attributes_by_ids(schema.product_attribute_ids or [])
        if len(attributes) != len(schema.product_attribute_ids or []):
            raise ValidationException(message="One or more Product Attributes are invalid")
            
        update_data = schema.model_dump(exclude_unset=True, exclude={"product_attribute_ids"})
        for key, value in update_data.items():
            setattr(item, key, value)
            
        item.product_attributes = attributes
        item.updated_by = updated_by
        return await self.repository.update(item)
        
    async def activate_item(self, item_id: UUID, updated_by: UUID) -> InventoryItemModel:
        item = await self.get_item(item_id)
        if item.status == GenericStatus.ACTIVE:
            raise ValidationException(message="Item is already active")
        item.status = GenericStatus.ACTIVE
        item.updated_by = updated_by
        return await self.repository.update(item)

    async def deactivate_item(self, item_id: UUID, updated_by: UUID) -> InventoryItemModel:
        item = await self.get_item(item_id)
        if item.status == GenericStatus.INACTIVE:
            raise ValidationException(message="Item is already inactive")
        item.status = GenericStatus.INACTIVE
        item.updated_by = updated_by
        return await self.repository.update(item)
        
    async def archive_item(self, item_id: UUID, updated_by: UUID) -> InventoryItemModel:
        item = await self.get_item(item_id)
        if item.status == GenericStatus.ARCHIVED:
            raise ValidationException(message="Item is already archived")
        item.status = GenericStatus.ARCHIVED
        item.updated_by = updated_by
        return await self.repository.update(item)
