from uuid import UUID
from typing import List, Tuple
from src.domains.masters.repositories.supplier import SupplierRepository
from src.domains.masters.models.supplier import Supplier
from src.domains.masters.schemas.supplier import SupplierCreate, SupplierUpdate
from src.foundation.exceptions.base import NotFoundException, ValidationException

class SupplierService:
    def __init__(self, repository: SupplierRepository):
        self.repository = repository

    async def get_by_id(self, supplier_id: UUID) -> Supplier:
        supplier = await self.repository.get_by_id(supplier_id)
        if not supplier:
            raise NotFoundException(message="Supplier not found")
        return supplier
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[Supplier], int]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create(self, schema: SupplierCreate, created_by: UUID) -> Supplier:
        if schema.gstin:
            existing = await self.repository.get_by_gstin(schema.gstin)
            if existing:
                raise ValidationException(message="Supplier with this GSTIN already exists")
                
        supplier = Supplier(
            **schema.model_dump(),
            created_by=created_by,
            updated_by=created_by
        )
        return await self.repository.create(supplier)

    async def update(self, supplier_id: UUID, schema: SupplierUpdate, updated_by: UUID) -> Supplier:
        supplier = await self.get_by_id(supplier_id)
        
        if schema.gstin:
            existing = await self.repository.get_by_gstin(schema.gstin)
            if existing and existing.id != supplier.id:
                raise ValidationException(message="Supplier with this GSTIN already exists")

        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(supplier, key, value)
            
        supplier.updated_by = updated_by
        return await self.repository.update(supplier)
        
    async def delete(self, supplier_id: UUID) -> None:
        supplier = await self.get_by_id(supplier_id)
        await self.repository.delete(supplier)
