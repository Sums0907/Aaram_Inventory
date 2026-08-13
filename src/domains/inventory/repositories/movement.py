from uuid import UUID
from typing import List, Optional
from datetime import date
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.schemas.movement import InventoryMovementCreate

class InventoryMovementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_movement(self, data: InventoryMovementCreate, created_by: UUID, session: AsyncSession = None) -> InventoryMovementModel:
        movement_dict = data.model_dump()
        movement_dict["created_by"] = created_by
        movement_dict["updated_by"] = created_by
        
        db_movement = InventoryMovementModel(**movement_dict)
        db_session = session or self.session
        db_session.add(db_movement)
        if not session:
            await db_session.commit()
            await db_session.refresh(db_movement)
        else:
            await db_session.flush()
        return db_movement
        
    async def get_by_movement_number(self, movement_number: str, session: AsyncSession = None) -> Optional[InventoryMovementModel]:
        db_session = session or self.session
        stmt = select(InventoryMovementModel).where(InventoryMovementModel.movement_number == movement_number)
        result = await db_session.execute(stmt)
        return result.scalars().first()
        
    async def get_balance(self, warehouse_id: UUID, sku_id: UUID, session: AsyncSession = None) -> Decimal:
        db_session = session or self.session
        stmt = select(func.sum(InventoryMovementModel.quantity)).where(
            InventoryMovementModel.warehouse_id == warehouse_id,
            InventoryMovementModel.sku_id == sku_id,
            InventoryMovementModel.status == "POSTED"
        )
        result = await db_session.execute(stmt)
        balance = result.scalar()
        return Decimal(str(balance)) if balance is not None else Decimal("0")

    async def get_movements_for_sku(self, sku_id: UUID) -> List[InventoryMovementModel]:
        stmt = (
            select(InventoryMovementModel)
            .where(
                InventoryMovementModel.sku_id == sku_id,
                InventoryMovementModel.status == "POSTED"
            )
            .order_by(InventoryMovementModel.posting_date.asc(), InventoryMovementModel.created_on.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_movements(self, limit: int = 10) -> List[InventoryMovementModel]:
        stmt = (
            select(InventoryMovementModel)
            .order_by(InventoryMovementModel.created_on.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_manual_adjustments_today_count(self) -> int:
        from datetime import date
        stmt = select(func.count(InventoryMovementModel.id)).where(
            InventoryMovementModel.movement_type == "MANUAL_ADJUSTMENT",
            InventoryMovementModel.movement_date == date.today()
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_activities_count(
        self, 
        movement_type: Optional[str] = None, 
        sku_id: Optional[UUID] = None,
        item_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> int:
        from src.domains.masters.models.sku import SKUModel
        from src.domains.masters.models.product import ProductModel
        
        stmt = select(func.count(InventoryMovementModel.id)).where(InventoryMovementModel.status == "POSTED")
        
        if item_type:
            stmt = stmt.join(SKUModel, SKUModel.id == InventoryMovementModel.sku_id)\
                       .join(ProductModel, ProductModel.id == SKUModel.product_id)\
                       .where(ProductModel.item_type == item_type)
            
        if movement_type:
            stmt = stmt.where(InventoryMovementModel.movement_type == movement_type)
        if sku_id:
            stmt = stmt.where(InventoryMovementModel.sku_id == sku_id)
        if date_from:
            stmt = stmt.where(InventoryMovementModel.movement_date >= date_from)
        if date_to:
            stmt = stmt.where(InventoryMovementModel.movement_date <= date_to)
            
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_activities(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        movement_type: Optional[str] = None, 
        sku_id: Optional[UUID] = None,
        item_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ):
        from src.domains.masters.models.sku import SKUModel
        from src.domains.masters.models.product import ProductModel
        
        # We use a CTE to calculate the running balance for each SKU
        balance_col = func.sum(InventoryMovementModel.quantity).over(
            partition_by=InventoryMovementModel.sku_id,
            order_by=(InventoryMovementModel.posting_date.asc(), InventoryMovementModel.created_on.asc())
        ).label('balance_after_activity')
        
        # Base query for CTE
        cte_stmt = select(InventoryMovementModel, balance_col).where(InventoryMovementModel.status == "POSTED")
        cte = cte_stmt.cte('movement_cte')
        
        # Main query joining with SKU and Product
        stmt = (
            select(
                cte,
                SKUModel.item_code.label("inventory_code"),
                ProductModel.product_name.label("item_name"),
                ProductModel.item_type.label("item_type")
            )
            .join(SKUModel, SKUModel.id == cte.c.sku_id)
            .join(ProductModel, ProductModel.id == SKUModel.product_id)
        )
        
        if item_type:
            stmt = stmt.where(ProductModel.item_type == item_type)
        if movement_type:
            stmt = stmt.where(cte.c.movement_type == movement_type)
        if sku_id:
            stmt = stmt.where(cte.c.sku_id == sku_id)
        if date_from:
            stmt = stmt.where(cte.c.movement_date >= date_from)
        if date_to:
            stmt = stmt.where(cte.c.movement_date <= date_to)
            
        stmt = stmt.order_by(cte.c.posting_date.desc(), cte.c.created_on.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(stmt)
        # Using mappings() returns row objects that behave like dicts, which is easier to work with CTE columns
        return result.mappings().all()
