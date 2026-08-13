from typing import List
from uuid import UUID
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.schemas.category import CategoryCreate, CategoryUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException
from src.foundation.enums.status import GenericStatus

class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def get_category(self, category_id: UUID) -> CategoryModel:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundException(message="Category not found")
        return category
        
    async def list_categories(self, skip: int = 0, limit: int = 100, item_type: str = None) -> List[CategoryModel]:
        return await self.repository.get_all(skip=skip, limit=limit, item_type=item_type)
        
    async def create_category(self, schema: CategoryCreate, created_by: UUID) -> CategoryModel:
        import uuid
        if not schema.category_code:
            schema.category_code = f"CAT-{uuid.uuid4().hex[:6].upper()}"

        # Business Validation: Uniqueness
        if await self.repository.get_by_code(schema.category_code):
            raise ValidationException(message="Category Code must be unique")
        if await self.repository.get_by_name(schema.category_name):
            raise ValidationException(message="Category Name must be unique")
            
        category = CategoryModel(
            **schema.model_dump(exclude={"attributes"}),
            created_by=created_by,
            updated_by=created_by
        )
        category = await self.repository.create(category)

        if schema.attributes is not None:
            await self.repository.set_category_attributes(category.id, schema.attributes)

        return await self.get_category(category.id)

    async def update_category(self, category_id: UUID, schema: CategoryUpdate, updated_by: UUID) -> CategoryModel:
        category = await self.get_category(category_id)
        
        # Business Validation: Uniqueness (Exclude self)
        existing_name = await self.repository.get_by_name(schema.category_name)
        if existing_name and existing_name.id != category.id:
            raise ValidationException(message="Category Name must be unique")

        # Apply updates
        update_data = schema.model_dump(exclude_unset=True, exclude={"attributes"})
        for key, value in update_data.items():
            setattr(category, key, value)
            
        category.updated_by = updated_by
        await self.repository.update(category)

        if schema.attributes is not None:
            await self.repository.set_category_attributes(category.id, schema.attributes)

        return await self.get_category(category.id)
        
    async def activate_category(self, category_id: UUID, updated_by: UUID) -> CategoryModel:
        category = await self.get_category(category_id)
        if category.status == GenericStatus.ACTIVE:
            raise ValidationException(message="Category is already active")
        category.status = GenericStatus.ACTIVE
        category.updated_by = updated_by
        return await self.repository.update(category)

    async def deactivate_category(self, category_id: UUID, updated_by: UUID) -> CategoryModel:
        category = await self.get_category(category_id)
        if category.status == GenericStatus.INACTIVE:
            raise ValidationException(message="Category is already inactive")
        category.status = GenericStatus.INACTIVE
        category.updated_by = updated_by
        return await self.repository.update(category)
        
    async def archive_category(self, category_id: UUID, updated_by: UUID) -> CategoryModel:
        category = await self.get_category(category_id)
        if category.status == GenericStatus.ARCHIVED:
            raise ValidationException(message="Category is already archived")
        category.status = GenericStatus.ARCHIVED
        category.updated_by = updated_by
        return await self.repository.update(category)
        
    async def delete_category(self, category_id: UUID) -> None:
        category = await self.get_category(category_id)
        if category.status != GenericStatus.ARCHIVED:
            raise ValidationException(message="Only archived categories can be permanently deleted")
        await self.repository.delete(category_id)
