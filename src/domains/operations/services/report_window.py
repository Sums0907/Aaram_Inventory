from typing import Callable, Optional
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.schemas.lifecycle import ShopDeckStatus, LifecycleState, DynamicReportWindowResponse

class DateProvider:
    """Injectable date provider for deterministic testing."""
    def today(self) -> date:
        return date.today()

class ShopDeckReportWindowService:
    def __init__(self, session: AsyncSession, date_provider: Optional[DateProvider] = None):
        self.session = session
        self.date_provider = date_provider or DateProvider()

    async def calculate_required_window(self) -> DynamicReportWindowResponse:
        current_date = self.date_provider.today()
        
        # Base condition for logically ACTIVE orders
        base_condition = and_(
            SalesOrderModel.lifecycle_state == LifecycleState.ACTIVE.value,
            or_(
                SalesOrderModel.status != ShopDeckStatus.DELIVERED.value,
                SalesOrderModel.return_watch_until >= current_date
            )
        )

        # 1. Get the total count of active orders
        count_stmt = select(func.count(SalesOrderModel.id)).where(base_condition)
        count_res = await self.session.execute(count_stmt)
        active_order_count = count_res.scalar() or 0

        # 2. Get the oldest active order
        if active_order_count > 0:
            oldest_stmt = (
                select(SalesOrderModel)
                .where(base_condition)
                .order_by(SalesOrderModel.order_date.asc(), SalesOrderModel.id.asc())
                .limit(1)
            )
            oldest_res = await self.session.execute(oldest_stmt)
            oldest_order = oldest_res.scalars().first()
            
            if oldest_order:
                start_date = oldest_order.order_date.date() if isinstance(oldest_order.order_date, datetime) else oldest_order.order_date
                
                return DynamicReportWindowResponse(
                    required_report_start_date=start_date,
                    required_report_end_date=current_date,
                    oldest_active_order_date=start_date,
                    oldest_active_order_id=str(oldest_order.id),
                    active_order_count=active_order_count,
                    reason=f"Report starts on {start_date.strftime('%d-%b-%Y')} because Order {oldest_order.id} is the oldest currently active inventory order."
                )
                
        # Fallback if no active orders
        return DynamicReportWindowResponse(
            required_report_start_date=None,
            required_report_end_date=None,
            oldest_active_order_date=None,
            oldest_active_order_id=None,
            active_order_count=0,
            reason="No active ShopDeck orders currently require monitoring."
        )
