import pytest
from uuid_extensions import uuid7
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.repositories.warehouse import WarehouseRepository
from src.domains.masters.services.warehouse import WarehouseService
from src.domains.masters.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from src.foundation.exceptions.base import ValidationException
from src.foundation.enums.status import GenericStatus

def get_base_schema(code, name):
    return WarehouseCreate(
        warehouse_code=code,
        warehouse_name=name,
        address_line_1="Street",
        city="City",
        state="State",
        pin_code="000000"
    )

@pytest.mark.asyncio
async def test_service_create_success(db_session: AsyncSession):
    repo = WarehouseRepository(db_session)
    service = WarehouseService(repo)
    user_id = uuid7()
    
    schema = get_base_schema("WH-1", "Warehouse 1")
    warehouse = await service.create_warehouse(schema, created_by=user_id)
    
    assert warehouse.id is not None
    assert warehouse.warehouse_code == "WH-1"
    assert warehouse.status == GenericStatus.ACTIVE

@pytest.mark.asyncio
async def test_service_create_duplicate_code(db_session: AsyncSession):
    repo = WarehouseRepository(db_session)
    service = WarehouseService(repo)
    user_id = uuid7()
    
    await service.create_warehouse(get_base_schema("WH-2", "Warehouse 2"), created_by=user_id)
    
    with pytest.raises(ValidationException) as exc:
        await service.create_warehouse(get_base_schema("WH-2", "Warehouse 3"), created_by=user_id)
    
    assert "Warehouse Code must be unique" in str(exc.value)

@pytest.mark.asyncio
async def test_service_status_lifecycle(db_session: AsyncSession):
    repo = WarehouseRepository(db_session)
    service = WarehouseService(repo)
    user_id = uuid7()
    
    warehouse = await service.create_warehouse(get_base_schema("WH-4", "Warehouse 4"), created_by=user_id)
    
    # Deactivate
    deactivated = await service.deactivate_warehouse(warehouse.id, updated_by=user_id)
    assert deactivated.status == GenericStatus.INACTIVE
    
    # Archive
    archived = await service.archive_warehouse(warehouse.id, updated_by=user_id)
    assert archived.status == GenericStatus.ARCHIVED
