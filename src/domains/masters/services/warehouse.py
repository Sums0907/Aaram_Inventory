from typing import List
from uuid import UUID
from src.domains.masters.repositories.warehouse import WarehouseRepository
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException
from src.foundation.enums.status import GenericStatus

class WarehouseService:
    def __init__(self, repository: WarehouseRepository):
        self.repository = repository

    async def get_warehouse(self, warehouse_id: UUID) -> WarehouseModel:
        warehouse = await self.repository.get_by_id(warehouse_id)
        if not warehouse:
            raise NotFoundException(message="Warehouse not found")
        return warehouse
        
    async def list_warehouses(self, skip: int = 0, limit: int = 100) -> List[WarehouseModel]:
        return await self.repository.get_all(skip=skip, limit=limit)
        
    async def create_warehouse(self, schema: WarehouseCreate, created_by: UUID) -> WarehouseModel:
        # Business Validation: Uniqueness
        if await self.repository.get_by_code(schema.warehouse_code):
            raise ValidationException(message="Warehouse Code must be unique")
        if await self.repository.get_by_name(schema.warehouse_name):
            raise ValidationException(message="Warehouse Name must be unique")
            
        warehouse = WarehouseModel(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(warehouse)

    async def update_warehouse(self, warehouse_id: UUID, schema: WarehouseUpdate, updated_by: UUID) -> WarehouseModel:
        warehouse = await self.get_warehouse(warehouse_id)
        
        # Business Validation: Uniqueness (Exclude self)
        existing_name = await self.repository.get_by_name(schema.warehouse_name)
        if existing_name and existing_name.id != warehouse.id:
            raise ValidationException(message="Warehouse Name must be unique")

        # Apply updates
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(warehouse, key, value)
            
        warehouse.updated_by = updated_by
        return await self.repository.update(warehouse)
        
    async def activate_warehouse(self, warehouse_id: UUID, updated_by: UUID) -> WarehouseModel:
        warehouse = await self.get_warehouse(warehouse_id)
        if warehouse.status == GenericStatus.ACTIVE:
            raise ValidationException(message="Warehouse is already active")
        warehouse.status = GenericStatus.ACTIVE
        warehouse.updated_by = updated_by
        return await self.repository.update(warehouse)

    async def deactivate_warehouse(self, warehouse_id: UUID, updated_by: UUID) -> WarehouseModel:
        warehouse = await self.get_warehouse(warehouse_id)
        if warehouse.status == GenericStatus.INACTIVE:
            raise ValidationException(message="Warehouse is already inactive")
        warehouse.status = GenericStatus.INACTIVE
        warehouse.updated_by = updated_by
        return await self.repository.update(warehouse)
        
    async def archive_warehouse(self, warehouse_id: UUID, updated_by: UUID) -> WarehouseModel:
        warehouse = await self.get_warehouse(warehouse_id)
        if warehouse.status == GenericStatus.ARCHIVED:
            raise ValidationException(message="Warehouse is already archived")
        warehouse.status = GenericStatus.ARCHIVED
        warehouse.updated_by = updated_by
        return await self.repository.update(warehouse)
