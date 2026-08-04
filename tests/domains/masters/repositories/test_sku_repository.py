import pytest
from uuid import uuid7
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.inventory_item import InventoryItemModel
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.repositories.sku import SKURepository
from src.domains.masters.repositories.inventory_item import InventoryItemRepository
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository

@pytest.mark.asyncio
async def test_repository_create_and_get(db_session: AsyncSession):
    cat_repo = CategoryRepository(db_session)
    uom_repo = UnitOfMeasureRepository(db_session)
    item_repo = InventoryItemRepository(db_session)
    sku_repo = SKURepository(db_session)
    
    cat = await cat_repo.create(CategoryModel(category_code="C1", category_name="Cat1"))
    uom = await uom_repo.create(UnitOfMeasureModel(unit_code="U1", unit_name="Unit1"))
    
    item = await item_repo.create(InventoryItemModel(
        item_code="ITM-1",
        item_name="Item 1",
        category_id=cat.id,
        unit_of_measure_id=uom.id,
        gst_rate=18.0
    ))
    
    sku = SKUModel(
        sku_code="SKU-1",
        sku_name="SKU 1",
        inventory_item_id=item.id,
        attribute_values={"Size": "M"},
        gst_rate=18.0
    )
    
    created = await sku_repo.create(sku)
    assert created.id is not None
    assert created.attribute_values["Size"] == "M"
    
    fetched = await sku_repo.get_by_code("SKU-1")
    assert fetched is not None
    assert fetched.id == created.id
