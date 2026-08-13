from datetime import date, datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.models.lifecycle import CustomerReturnPolicyModel, OrderStateTransitionModel
from src.domains.operations.schemas.lifecycle import ShopDeckStatus, LifecycleState

class UnknownShopDeckStatusException(Exception):
    def __init__(self, status: str):
        super().__init__(f"Unknown ShopDeck status: {status}")
        self.status = status


class LifecycleEngine:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_return_policy(self) -> CustomerReturnPolicyModel:
        stmt = select(CustomerReturnPolicyModel).where(CustomerReturnPolicyModel.is_active == True).order_by(CustomerReturnPolicyModel.effective_from.desc())
        res = await self.session.execute(stmt)
        policy = res.scalars().first()
        if not policy:
            # Fallback default if not configured (as per requirement: 7 days)
            policy = CustomerReturnPolicyModel(
                effective_from=date.today(),
                return_window_days=7,
                is_active=True
            )
            self.session.add(policy)
            await self.session.flush()
        return policy

    def _determine_lifecycle_state(self, status: str, return_watch_until: Optional[date], current_date: date) -> LifecycleState:
        try:
            enum_status = ShopDeckStatus(status)
        except ValueError:
            raise UnknownShopDeckStatusException(status)

        if enum_status in [ShopDeckStatus.PRINT, ShopDeckStatus.PACK, ShopDeckStatus.IN_TRANSIT, 
                           ShopDeckStatus.HANDOVER, ShopDeckStatus.RTO_ACKNOWLEDGED, ShopDeckStatus.RTO_INITIATED,
                           ShopDeckStatus.PENDING]:
            return LifecycleState.ACTIVE
            
        elif enum_status in [ShopDeckStatus.RTO_DELIVERED, ShopDeckStatus.RETURNED, ShopDeckStatus.CANCELLED_INITIATED,
                             ShopDeckStatus.EXPIRED_AWB, ShopDeckStatus.LOST]:
            return LifecycleState.TERMINAL
            
        elif enum_status == ShopDeckStatus.DELIVERED:
            if return_watch_until and current_date > return_watch_until:
                return LifecycleState.TERMINAL
            return LifecycleState.ACTIVE
            
        raise UnknownShopDeckStatusException(status)

    async def process_shopdeck_status_update(
        self, 
        order: SalesOrderModel, 
        new_status: str, 
        observed_at: datetime, 
        source_reference: Optional[str] = None,
        transition_type: str = "STATE_TRANSITION"
    ) -> Tuple[bool, LifecycleState]:
        """
        Processes a status update for a ShopDeck order.
        Returns a tuple: (did_transition_occur, resulting_lifecycle_state)
        """
        try:
            _ = ShopDeckStatus(new_status)
        except ValueError:
            raise UnknownShopDeckStatusException(new_status)

        current_date = observed_at.date()
        
        # Determine if there's an actual status change or if it's identical
        is_new_transition = False
        
        if getattr(order, "status", None) != new_status or getattr(order, "last_observed_at", None) != observed_at:
            # Idempotency check:
            # "Repeatedly uploading the same ShopDeck report must produce: 0 duplicate transitions"
            
            stmt = select(OrderStateTransitionModel).where(
                OrderStateTransitionModel.external_order_id == order.external_order_id,
                OrderStateTransitionModel.new_status == new_status,
                OrderStateTransitionModel.observed_at == observed_at
            )
            res = await self.session.execute(stmt)
            existing_transition = res.scalars().first()
            
            if not existing_transition and getattr(order, "status", None) != new_status:
                is_new_transition = True
                
        if is_new_transition:
            transition = OrderStateTransitionModel(
                order_id=order.id,
                external_order_id=order.external_order_id,
                old_status=getattr(order, "status", None),
                new_status=new_status,
                observed_at=observed_at,
                source_reference=source_reference,
                transition_type=transition_type
            )
            self.session.add(transition)

            order.status = new_status
            order.last_observed_at = observed_at

        # Special logic for DELIVERED
        if new_status == ShopDeckStatus.DELIVERED.value and order.delivered_date is None:
            order.delivered_date = current_date
            policy = await self.get_active_return_policy()
            order.return_policy_id = policy.id
            order.return_window_days_at_delivery = policy.return_window_days
            order.return_watch_until = current_date + timedelta(days=policy.return_window_days)

        # Derive Lifecycle State
        new_lifecycle_state = self._determine_lifecycle_state(new_status, order.return_watch_until, current_date)
        
        if new_lifecycle_state == LifecycleState.TERMINAL and order.terminal_date is None:
            order.terminal_date = current_date

        order.lifecycle_state = new_lifecycle_state.value
        
        return (is_new_transition, new_lifecycle_state)
