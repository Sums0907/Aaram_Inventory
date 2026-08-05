import pytest
from uuid_extensions import uuid7
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.repositories.sku import SKURepository
from src.domains.masters.repositories.inventory_item import InventoryItemRepository
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository
from src.domains.masters.services.sku import SKUService
from src.domains.masters.schemas.sku import SKUCreate
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.inventory_item import InventoryItemModel
from src.foundation.exceptions.base import ValidationException

@pytest.mark.asyncio
async def test_service_create_success_and_unique_attributes(db_session: AsyncSession):
    sku_repo = SKURepository(db_session)
    item_repo = InventoryItemRepository(db_session)
    cat_repo = CategoryRepository(db_session)
    uom_repo = UnitOfMeasureRepository(db_session)
    service = SKUService(sku_repo, item_repo)
    user_id = uuid7()
    
    cat = await cat_repo.create(CategoryModel(category_code="CAT-SVC", category_name="SVC Cat"))
    uom = await uom_repo.create(UnitOfMeasureModel(unit_code="UOM-SVC", unit_name="SVC Uom", short_name="SVC"))
    item = await item_repo.create(InventoryItemModel(
        item_code="ITM-SVC", item_name="SVC Item", category_id=cat.id, unit_of_measure_id=uom.id, gst_rate=18.0
    ))
    
    schema = SKUCreate(
        sku_code="SKU-SVC-1",
        sku_name="SVC SKU 1",
        inventory_item_id=item.id,
        attribute_values={"Size": "L"},
        gst_rate=12.0
    )
    
    sku = await service.create_sku(schema, created_by=user_id)
    assert sku.sku_code == "SKU-SVC-1"
    
    # Try duplicate attributes
    schema2 = SKUCreate(
        sku_code="SKU-SVC-2",
        sku_name="SVC SKU 2",
        inventory_item_id=item.id,
        attribute_values={"Size": "L"}, # Duplicate!
        gst_rate=12.0
    )
    
    with pytest.raises(ValidationException) as exc:
        await service.create_sku(schema2, created_by=user_id)
        
    assert "Attribute combination must be unique" in str(exc.value)
