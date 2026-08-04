import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository

@pytest.mark.asyncio
async def test_repository_create_and_get(db_session: AsyncSession):
    repo = UnitOfMeasureRepository(db_session)
    
    uom = UnitOfMeasureModel(
        unit_code="BOX",
        unit_name="Boxes",
        short_name="box"
    )
    created_uom = await repo.create(uom)
    
    assert created_uom.id is not None
    assert created_uom.unit_code == "BOX"
    
    fetched_uom = await repo.get_by_code("BOX")
    assert fetched_uom is not None
    assert fetched_uom.id == created_uom.id

@pytest.mark.asyncio
async def test_repository_get_all(db_session: AsyncSession):
    repo = UnitOfMeasureRepository(db_session)
    
    await repo.create(UnitOfMeasureModel(unit_code="MTR", unit_name="Meters", short_name="mtr"))
    await repo.create(UnitOfMeasureModel(unit_code="LTR", unit_name="Liters", short_name="ltr"))
    
    results = await repo.get_all()
    assert len(results) >= 2
    codes = [u.unit_code for u in results]
    assert "MTR" in codes
    assert "LTR" in codes
