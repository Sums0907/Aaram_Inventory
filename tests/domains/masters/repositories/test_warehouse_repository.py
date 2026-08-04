import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.repositories.warehouse import WarehouseRepository

@pytest.mark.asyncio
async def test_repository_create_and_get(db_session: AsyncSession):
    repo = WarehouseRepository(db_session)
    
    warehouse = WarehouseModel(
        warehouse_code="PUN-01",
        warehouse_name="Pune Storage",
        address_line_1="Street 1",
        city="Pune",
        state="MH",
        country="India",
        pin_code="411001"
    )
    created_warehouse = await repo.create(warehouse)
    
    assert created_warehouse.id is not None
    assert created_warehouse.warehouse_code == "PUN-01"
    
    fetched = await repo.get_by_code("PUN-01")
    assert fetched is not None
    assert fetched.id == created_warehouse.id

@pytest.mark.asyncio
async def test_repository_get_all(db_session: AsyncSession):
    repo = WarehouseRepository(db_session)
    
    await repo.create(WarehouseModel(warehouse_code="BLR-01", warehouse_name="Bangalore Store", address_line_1="A", city="B", state="KA", country="India", pin_code="560001"))
    await repo.create(WarehouseModel(warehouse_code="CHE-01", warehouse_name="Chennai Store", address_line_1="C", city="C", state="TN", country="India", pin_code="600001"))
    
    results = await repo.get_all()
    assert len(results) >= 2
    codes = [w.warehouse_code for w in results]
    assert "BLR-01" in codes
    assert "CHE-01" in codes
