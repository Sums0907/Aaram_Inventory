import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.inventory_item import InventoryItemModel
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.product_attribute import ProductAttributeModel
from src.domains.masters.repositories.inventory_item import InventoryItemRepository
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository
from src.domains.masters.repositories.product_attribute import ProductAttributeRepository

@pytest.mark.asyncio
async def test_repository_create_and_get(db_session: AsyncSession):
    cat_repo = CategoryRepository(db_session)
    uom_repo = UnitOfMeasureRepository(db_session)
    attr_repo = ProductAttributeRepository(db_session)
    item_repo = InventoryItemRepository(db_session)
    
    cat = await cat_repo.create(CategoryModel(category_code="C1", category_name="Cat1"))
    uom = await uom_repo.create(UnitOfMeasureModel(unit_code="U1", unit_name="Unit1", short_name="U1"))
    attr = await attr_repo.create(ProductAttributeModel(attribute_code="A1", attribute_name="Attr1"))
    
    item = InventoryItemModel(
        item_code="ITM-01",
        item_name="Item 1",
        category_id=cat.id,
        unit_of_measure_id=uom.id,
        gst_rate=18.0,
        product_attributes=[attr]
    )
    
    created = await item_repo.create(item)
    assert created.id is not None
    assert len(created.product_attributes) == 1
    
    fetched = await item_repo.get_by_code("ITM-01")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.product_attributes[0].id == attr.id
