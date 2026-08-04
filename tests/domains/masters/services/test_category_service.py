import pytest
from uuid import uuid7
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.services.category import CategoryService
from src.domains.masters.schemas.category import CategoryCreate
from src.foundation.exceptions.base import ValidationException
from src.foundation.enums.status import GenericStatus

@pytest.mark.asyncio
async def test_service_create_success(db_session: AsyncSession):
    repo = CategoryRepository(db_session)
    service = CategoryService(repo)
    user_id = uuid7()
    
    schema = CategoryCreate(category_code="CAT-A", category_name="Category A")
    category = await service.create_category(schema, created_by=user_id)
    
    assert category.id is not None
    assert category.category_code == "CAT-A"
    assert category.status == GenericStatus.ACTIVE

@pytest.mark.asyncio
async def test_service_create_duplicate_code(db_session: AsyncSession):
    repo = CategoryRepository(db_session)
    service = CategoryService(repo)
    user_id = uuid7()
    
    await service.create_category(CategoryCreate(category_code="CAT-B", category_name="Category B"), created_by=user_id)
    
    with pytest.raises(ValidationException) as exc:
        await service.create_category(CategoryCreate(category_code="CAT-B", category_name="Category C"), created_by=user_id)
    
    assert "Category Code must be unique" in str(exc.value)

@pytest.mark.asyncio
async def test_service_status_lifecycle(db_session: AsyncSession):
    repo = CategoryRepository(db_session)
    service = CategoryService(repo)
    user_id = uuid7()
    
    category = await service.create_category(CategoryCreate(category_code="CAT-D", category_name="Category D"), created_by=user_id)
    
    deactivated = await service.deactivate_category(category.id, updated_by=user_id)
    assert deactivated.status == GenericStatus.INACTIVE
    
    archived = await service.archive_category(category.id, updated_by=user_id)
    assert archived.status == GenericStatus.ARCHIVED
