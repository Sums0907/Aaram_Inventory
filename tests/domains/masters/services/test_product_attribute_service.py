import pytest
from uuid_extensions import uuid7
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.repositories.product_attribute import ProductAttributeRepository
from src.domains.masters.services.product_attribute import ProductAttributeService
from src.domains.masters.schemas.product_attribute import ProductAttributeCreate
from src.foundation.exceptions.base import ValidationException
from src.foundation.enums.status import GenericStatus

@pytest.mark.asyncio
async def test_service_create_success(db_session: AsyncSession):
    repo = ProductAttributeRepository(db_session)
    service = ProductAttributeService(repo)
    user_id = uuid7()
    
    schema = ProductAttributeCreate(attribute_code="ATTR-A", attribute_name="Attribute A")
    attribute = await service.create_attribute(schema, created_by=user_id)
    
    assert attribute.id is not None
    assert attribute.attribute_code == "ATTR-A"
    assert attribute.status == GenericStatus.ACTIVE

@pytest.mark.asyncio
async def test_service_create_duplicate_code(db_session: AsyncSession):
    repo = ProductAttributeRepository(db_session)
    service = ProductAttributeService(repo)
    user_id = uuid7()
    
    await service.create_attribute(ProductAttributeCreate(attribute_code="ATTR-B", attribute_name="Attribute B"), created_by=user_id)
    
    with pytest.raises(ValidationException) as exc:
        await service.create_attribute(ProductAttributeCreate(attribute_code="ATTR-B", attribute_name="Attribute C"), created_by=user_id)
    
    assert "Attribute Code must be unique" in str(exc.value)

@pytest.mark.asyncio
async def test_service_status_lifecycle(db_session: AsyncSession):
    repo = ProductAttributeRepository(db_session)
    service = ProductAttributeService(repo)
    user_id = uuid7()
    
    attribute = await service.create_attribute(ProductAttributeCreate(attribute_code="ATTR-D", attribute_name="Attribute D"), created_by=user_id)
    
    deactivated = await service.deactivate_attribute(attribute.id, updated_by=user_id)
    assert deactivated.status == GenericStatus.INACTIVE
    
    archived = await service.archive_attribute(attribute.id, updated_by=user_id)
    assert archived.status == GenericStatus.ARCHIVED
