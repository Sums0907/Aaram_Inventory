import os
import httpx
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.inventory.models.outbox import InventoryOutboundEventModel

logger = logging.getLogger(__name__)

class OutboundEventDispatcherService:
    def __init__(self):
        # Determine Packer URL, fallback to default port 8001 based on shell script
        self.packer_url = os.getenv("PACKER_SERVICE_URL", "http://127.0.0.1:8001")
        self.webhook_endpoint = f"{self.packer_url}/api/v1/internal/webhooks/inventory/events"
        self.max_retries = 5

    async def dispatch_pending_events(self, session: AsyncSession):
        """
        Polls the database for PENDING or eligible FAILED events,
        and dispatches them to the Packer Webhook with exponential backoff.
        """
        now = datetime.now(timezone.utc)
        
        # Fetch events that are PENDING or (FAILED and due for retry)
        stmt = select(InventoryOutboundEventModel).where(
            or_(
                InventoryOutboundEventModel.status == "PENDING",
                (InventoryOutboundEventModel.status == "FAILED") & 
                (InventoryOutboundEventModel.retry_count < self.max_retries) & 
                (InventoryOutboundEventModel.next_attempt_at <= now)
            )
        ).order_by(InventoryOutboundEventModel.created_on.asc()).limit(100).with_for_update(skip_locked=True)
        
        result = await session.execute(stmt)
        events = result.scalars().all()

        if not events:
            return

        async with httpx.AsyncClient(timeout=10.0) as client:
            for event in events:
                event.status = "PROCESSING"
                await session.commit() # Lock the event to prevent concurrent processing
                
                try:
                    # Construct Payload conforming to the generic webhook event envelope
                    webhook_payload = {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "aggregate_type": event.aggregate_type,
                        "aggregate_id": event.aggregate_id,
                        "payload": event.payload_json,
                        "timestamp": event.created_on.isoformat()
                    }
                    
                    headers = {"Content-Type": "application/json"}
                    # Use service-to-service API token
                    api_token = os.getenv("PACKER_API_TOKEN", "")
                    if api_token:
                        headers["Authorization"] = f"Bearer {api_token}"
                    
                    response = await client.post(self.webhook_endpoint, json=webhook_payload, headers=headers)
                    event.last_http_status = response.status_code
                    
                    if response.is_success:
                        event.status = "DELIVERED"
                        event.processed_at = datetime.now(timezone.utc)
                        event.last_error = None
                    else:
                        self._handle_failure(event, f"HTTP {response.status_code}: {response.text}")
                        
                except httpx.RequestError as exc:
                    event.last_http_status = None
                    self._handle_failure(event, f"Network Error: {str(exc)}")
                    
                except Exception as e:
                    event.last_http_status = None
                    self._handle_failure(event, f"Internal Error: {str(e)}")
                    
                await session.commit()

    def _handle_failure(self, event: InventoryOutboundEventModel, error_msg: str):
        event.retry_count += 1
        event.last_error = error_msg
        
        if event.retry_count >= self.max_retries:
            event.status = "DEAD_LETTER" # Dead letter handling, won't be retried
            logger.error(f"Outbound Event {event.event_id} moved to DEAD_LETTER: {error_msg}")
        else:
            event.status = "FAILED"
            # Exponential backoff: 5s, 30s, 5m, etc.
            backoff_seconds = (5 ** event.retry_count)
            event.next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_seconds)
            logger.warning(f"Outbound Event {event.event_id} FAILED (Retry {event.retry_count}): {error_msg}")
