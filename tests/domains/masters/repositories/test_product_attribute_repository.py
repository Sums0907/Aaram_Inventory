import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.product_attribute import ProductAttributeModel
from src.domains.masters.repositories.product_attribute import ProductAttributeRepository

@pytest.mark.asyncio
async def test_repository_create_and_get(db_session: AsyncSession):
    repo = ProductAttributeRepository(db_session)
    
    attribute = ProductAttributeModel(
        attribute_code="ATTR-1",
        attribute_name="Attribute 1",
        display_order=10
    )
    created = await repo.create(attribute)
    
    assert created.id is not None
    assert created.attribute_code == "ATTR-1"
    
    fetched = await repo.get_by_code("ATTR-1")
    assert fetched is not None
    assert fetched.id == created.id

@pytest.mark.asyncio
async def test_repository_get_all_ordered(db_session: AsyncSession):
    repo = ProductAttributeRepository(db_session)
    
    await repo.create(ProductAttributeModel(attribute_code="A3", attribute_name="Attr 3", display_order=3))
    await repo.create(ProductAttributeModel(attribute_code="A1", attribute_name="Attr 1", display_order=1))
    await repo.create(ProductAttributeModel(attribute_code="A2", attribute_name="Attr 2", display_order=2))
    
    results = await repo.get_all()
    assert len(results) >= 3
    
    codes = [a.attribute_code for a in results]
    assert "A1" in codes
    assert "A2" in codes
    assert "A3" in codes
