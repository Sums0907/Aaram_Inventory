import pytest
from uuid import uuid7
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.repositories.inventory_item import InventoryItemRepository
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository
from src.domains.masters.repositories.product_attribute import ProductAttributeRepository
from src.domains.masters.services.inventory_item import InventoryItemService
from src.domains.masters.schemas.inventory_item import InventoryItemCreate
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.product_attribute import ProductAttributeModel
from src.foundation.exceptions.base import ValidationException

@pytest.mark.asyncio
async def test_service_create_invalid_category(db_session: AsyncSession):
    item_repo = InventoryItemRepository(db_session)
    cat_repo = CategoryRepository(db_session)
    uom_repo = UnitOfMeasureRepository(db_session)
    service = InventoryItemService(item_repo, cat_repo, uom_repo)
    user_id = uuid7()
    
    schema = InventoryItemCreate(
        item_code="ITM-A",
        item_name="Item A",
        category_id=uuid7(), # Non-existent
        unit_of_measure_id=uuid7(),
        gst_rate=5.0
    )
    
    with pytest.raises(ValidationException) as exc:
        await service.create_item(schema, created_by=user_id)
        
    assert "Valid and Active Category is required" in str(exc.value)

@pytest.mark.asyncio
async def test_service_create_success(db_session: AsyncSession):
    item_repo = InventoryItemRepository(db_session)
    cat_repo = CategoryRepository(db_session)
    uom_repo = UnitOfMeasureRepository(db_session)
    attr_repo = ProductAttributeRepository(db_session)
    service = InventoryItemService(item_repo, cat_repo, uom_repo)
    user_id = uuid7()
    
    cat = await cat_repo.create(CategoryModel(category_code="CAT-SVC", category_name="SVC Cat"))
    uom = await uom_repo.create(UnitOfMeasureModel(unit_code="UOM-SVC", unit_name="SVC Uom"))
    attr = await attr_repo.create(ProductAttributeModel(attribute_code="ATTR-SVC", attribute_name="SVC Attr"))
    
    schema = InventoryItemCreate(
        item_code="ITM-B",
        item_name="Item B",
        category_id=cat.id,
        unit_of_measure_id=uom.id,
        gst_rate=12.0,
        product_attribute_ids=[attr.id]
    )
    
    item = await service.create_item(schema, created_by=user_id)
    assert item.item_code == "ITM-B"
    assert len(item.product_attributes) == 1
