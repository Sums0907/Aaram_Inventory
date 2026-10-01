import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class OutboundEventDispatcherService:
    """
    DEPRECATED: Packer has been detached from Inventory SKU and stock sync.
    This service is retained as a safe no-op to prevent broken imports.
    """
    def __init__(self):
        pass

    async def dispatch_pending_events(self, session: AsyncSession):
        """No-op: Packer sync has been decommissioned."""
        return
