import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifecycle manager. 
    Code before yield runs on startup. 
    Code after yield runs on shutdown.
    """
    logger.info("Aaram Inventory service started.")
    yield
    logger.info("Aaram Inventory service shut down cleanly.")
