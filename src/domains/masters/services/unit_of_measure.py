from typing import List
from uuid import UUID
from src.domains.masters.repositories.unit_of_measure import UnitOfMeasureRepository
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.schemas.unit_of_measure import UnitOfMeasureCreate, UnitOfMeasureUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException
from src.foundation.enums.status import GenericStatus

class UnitOfMeasureService:
    def __init__(self, repository: UnitOfMeasureRepository):
        self.repository = repository

    async def get_unit(self, unit_id: UUID) -> UnitOfMeasureModel:
        unit = await self.repository.get_by_id(unit_id)
        if not unit:
            raise NotFoundException(message="Unit of Measure not found")
        return unit
        
    async def list_units(self, skip: int = 0, limit: int = 100) -> List[UnitOfMeasureModel]:
        return await self.repository.get_all(skip=skip, limit=limit)
        
    async def create_unit(self, schema: UnitOfMeasureCreate, created_by: UUID) -> UnitOfMeasureModel:
        # Business Validation: Uniqueness
        if await self.repository.get_by_code(schema.unit_code):
            raise ValidationException(message="Unit Code must be unique")
        if await self.repository.get_by_name(schema.unit_name):
            raise ValidationException(message="Unit Name must be unique")
        if await self.repository.get_by_short_name(schema.short_name):
            raise ValidationException(message="Short Name must be unique")
            
        unit = UnitOfMeasureModel(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(unit)

    async def update_unit(self, unit_id: UUID, schema: UnitOfMeasureUpdate, updated_by: UUID) -> UnitOfMeasureModel:
        unit = await self.get_unit(unit_id)
        
        # Business Validation: Uniqueness (Exclude self)
        existing_name = await self.repository.get_by_name(schema.unit_name)
        if existing_name and existing_name.id != unit.id:
            raise ValidationException(message="Unit Name must be unique")
            
        existing_short_name = await self.repository.get_by_short_name(schema.short_name)
        if existing_short_name and existing_short_name.id != unit.id:
            raise ValidationException(message="Short Name must be unique")

        # Apply updates
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(unit, key, value)
            
        unit.updated_by = updated_by
        return await self.repository.update(unit)
        
    async def activate_unit(self, unit_id: UUID, updated_by: UUID) -> UnitOfMeasureModel:
        unit = await self.get_unit(unit_id)
        if unit.status == GenericStatus.ACTIVE:
            raise ValidationException(message="Unit of Measure is already active")
        unit.status = GenericStatus.ACTIVE
        unit.updated_by = updated_by
        return await self.repository.update(unit)

    async def deactivate_unit(self, unit_id: UUID, updated_by: UUID) -> UnitOfMeasureModel:
        unit = await self.get_unit(unit_id)
        if unit.status == GenericStatus.INACTIVE:
            raise ValidationException(message="Unit of Measure is already inactive")
        unit.status = GenericStatus.INACTIVE
        unit.updated_by = updated_by
        return await self.repository.update(unit)
        
    async def archive_unit(self, unit_id: UUID, updated_by: UUID) -> UnitOfMeasureModel:
        unit = await self.get_unit(unit_id)
        if unit.status == GenericStatus.ARCHIVED:
            raise ValidationException(message="Unit of Measure is already archived")
        unit.status = GenericStatus.ARCHIVED
        unit.updated_by = updated_by
        return await self.repository.update(unit)
