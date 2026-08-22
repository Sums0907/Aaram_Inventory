import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.container import DomainsContainer

logger = logging.getLogger(__name__)

# Global event to signal background tasks to shut down cleanly
shutdown_event = asyncio.Event()

async def run_outbox_dispatcher_loop(app: FastAPI):
    """Polls the outbox table every 30 seconds and dispatches events to Packer."""
    from src.domains.inventory.services.outbound_event_publisher import OutboundEventDispatcherService
    
    logger.info("Outbox Dispatcher background task started.")
    dispatcher = OutboundEventDispatcherService()
    
    # Extract the async session factory from the dependency injection container
    async_session_factory = app.core_container.db()._session_factory
    
    while not shutdown_event.is_set():
        try:
            async with async_session_factory() as session:
                await dispatcher.dispatch_pending_events(session)
        except Exception as e:
            logger.error(f"Error in Outbox Dispatcher loop: {e}", exc_info=True)
            
        # Wait 30 seconds before polling again, but wake up immediately if shutting down
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=30.0)
        except asyncio.TimeoutError:
            pass # Normal timeout, continue looping

async def run_daily_reconciliation_loop(app: FastAPI):
    """Runs the daily SKU master snapshot sync once every 24 hours relative to server start."""
    from src.domains.inventory.tasks.daily_reconciliation import run_daily_sku_reconciliation
    
    logger.info("Daily Reconciliation background task started.")
    async_session_factory = app.core_container.db()._session_factory
    
    # 24 hours in seconds
    WAIT_SECONDS = 24 * 60 * 60
    
    while not shutdown_event.is_set():
        try:
            async with async_session_factory() as session:
                await run_daily_sku_reconciliation(session)
        except Exception as e:
            logger.error(f"Error in Daily Reconciliation loop: {e}", exc_info=True)
            
        # Wait 24 hours, but wake up immediately if shutting down
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=WAIT_SECONDS)
        except asyncio.TimeoutError:
            pass # Normal timeout, continue looping


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifecycle manager. 
    Code before yield runs on startup. 
    Code after yield runs on shutdown.
    """
    logger.info("Starting up background tasks...")
    shutdown_event.clear()
    
    # Spawn the background tasks. 
    # These run concurrently and will not block incoming API requests.
    dispatcher_task = asyncio.create_task(run_outbox_dispatcher_loop(app))
    reconciliation_task = asyncio.create_task(run_daily_reconciliation_loop(app))
    
    yield # Application serves requests here
    
    logger.info("Shutting down background tasks...")
    # Signal the loops to break
    shutdown_event.set()
    
    # Wait gracefully for tasks to finish their current loop (up to 5 seconds)
    _, pending = await asyncio.wait([dispatcher_task, reconciliation_task], timeout=5.0)
    
    # Force cancel any tasks that refused to exit cleanly
    for task in pending:
        task.cancel()
    
    logger.info("Background tasks shut down successfully.")
