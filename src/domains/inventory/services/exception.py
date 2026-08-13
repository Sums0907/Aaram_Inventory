from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from src.domains.inventory.repositories.exception import InventoryExceptionRepository
from src.domains.inventory.models.exception import InventoryExceptionModel
from src.foundation.exceptions.base import NotFoundException

class InventoryExceptionService:
    def __init__(self, repository: InventoryExceptionRepository):
        self.repository = repository
        
    async def get_all_open_exceptions(self, limit: int = 50):
        # Return enriched data with SKU info for the UI
        # We can write a custom query here or in repo
        from src.domains.masters.models.sku import SKUModel
        from src.domains.masters.models.product import ProductModel
        
        stmt = (
            select(
                InventoryExceptionModel,
                SKUModel.item_code.label("inventory_code"),
                ProductModel.product_name.label("item_name")
            )
            .join(SKUModel, SKUModel.id == InventoryExceptionModel.sku_id)
            .join(ProductModel, ProductModel.id == SKUModel.product_id)
            .where(InventoryExceptionModel.status == "OPEN")
            .order_by(InventoryExceptionModel.exception_date.desc())
            .limit(limit)
        )
        
        result = await self.repository.session.execute(stmt)
        rows = result.all()
        
        exceptions = []
        for row in rows:
            exception_obj = row[0]
            exception_dict = {
                "id": exception_obj.id,
                "exception_number": exception_obj.exception_number,
                "warehouse_id": exception_obj.warehouse_id,
                "sku_id": exception_obj.sku_id,
                "exception_date": exception_obj.exception_date,
                "source_system": exception_obj.source_system,
                "expected_quantity": exception_obj.expected_quantity,
                "actual_quantity": exception_obj.actual_quantity,
                "difference": exception_obj.difference,
                "status": exception_obj.status,
                "resolution_notes": exception_obj.resolution_notes,
                "created_on": exception_obj.created_on,
                "inventory_item": {
                    "inventory_code": row.inventory_code,
                    "name": row.item_name
                }
            }
            exceptions.append(exception_dict)
            
        return exceptions

    async def resolve_exception(self, exception_id: UUID, resolution_notes: str):
        stmt = select(InventoryExceptionModel).where(InventoryExceptionModel.id == exception_id)
        result = await self.repository.session.execute(stmt)
        exception = result.scalars().first()
        
        if not exception:
            raise NotFoundException(message="Exception not found")
            
        exception.status = "RESOLVED"
        exception.resolution_notes = resolution_notes
        
        await self.repository.save(exception)
        return exception
