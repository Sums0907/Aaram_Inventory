import pytest
from uuid import uuid7
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository
from src.domains.masters.services.unit_of_measure import UnitOfMeasureService
from src.domains.masters.schemas.unit_of_measure import UnitOfMeasureCreate, UnitOfMeasureUpdate
from src.foundation.exceptions.base import ValidationException
from src.foundation.enums.status import GenericStatus

@pytest.mark.asyncio
async def test_service_create_success(db_session: AsyncSession):
    repo = UnitOfMeasureRepository(db_session)
    service = UnitOfMeasureService(repo)
    user_id = uuid7()
    
    schema = UnitOfMeasureCreate(unit_code="KG", unit_name="Kilograms", short_name="kg")
    uom = await service.create_unit(schema, created_by=user_id)
    
    assert uom.id is not None
    assert uom.unit_code == "KG"
    assert uom.status == GenericStatus.ACTIVE

@pytest.mark.asyncio
async def test_service_create_duplicate_code(db_session: AsyncSession):
    repo = UnitOfMeasureRepository(db_session)
    service = UnitOfMeasureService(repo)
    user_id = uuid7()
    
    schema1 = UnitOfMeasureCreate(unit_code="GM", unit_name="Grams", short_name="gm")
    await service.create_unit(schema1, created_by=user_id)
    
    schema2 = UnitOfMeasureCreate(unit_code="GM", unit_name="Grams Two", short_name="gm2")
    with pytest.raises(ValidationException) as exc:
        await service.create_unit(schema2, created_by=user_id)
    
    assert "Unit Code must be unique" in str(exc.value)

@pytest.mark.asyncio
async def test_service_status_lifecycle(db_session: AsyncSession):
    repo = UnitOfMeasureRepository(db_session)
    service = UnitOfMeasureService(repo)
    user_id = uuid7()
    
    schema = UnitOfMeasureCreate(unit_code="DOZ", unit_name="Dozen", short_name="dz")
    uom = await service.create_unit(schema, created_by=user_id)
    
    # Deactivate
    deactivated = await service.deactivate_unit(uom.id, updated_by=user_id)
    assert deactivated.status == GenericStatus.INACTIVE
    
    # Archive
    archived = await service.archive_unit(uom.id, updated_by=user_id)
    assert archived.status == GenericStatus.ARCHIVED
