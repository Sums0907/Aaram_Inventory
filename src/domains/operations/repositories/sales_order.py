from uuid import UUID
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.operations.models.sales_order import SalesOrderModel, SalesOrderItemModel
from src.domains.operations.schemas.sales_order import SalesOrderCreate


class SalesOrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_order(self, data: SalesOrderCreate, created_by: UUID) -> SalesOrderModel:
        order_dict = data.model_dump(exclude={"items"})
        order_dict["created_by"] = created_by
        order_dict["updated_by"] = created_by
        
        db_order = SalesOrderModel(**order_dict)
        
        for item_data in data.items:
            item_dict = item_data.model_dump()
            item_dict["created_by"] = created_by
            item_dict["updated_by"] = created_by
            db_item = SalesOrderItemModel(**item_dict)
            db_order.items.append(db_item)
            
        self.session.add(db_order)
        await self.session.commit()
        await self.session.refresh(db_order)
        return db_order
        
    async def get_by_external_id(self, external_order_id: str) -> SalesOrderModel | None:
        stmt = select(SalesOrderModel).where(SalesOrderModel.external_order_id == external_order_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()
