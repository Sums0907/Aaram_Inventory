import asyncio
from src.app.container import DomainsContainer
from src.foundation.logging.context import set_request_id
from src.foundation.configuration import get_settings
import logging

logging.basicConfig(level=logging.DEBUG)

async def main():
    set_request_id("test")
    container = DomainsContainer()
    container.core.config.from_dict(get_settings().model_dump())
    
    print("Getting service...")
    sku_service = container.masters.sku_service()
    print("Calling get_all on repo...")
    skus = await sku_service.repository.get_all(skip=0, limit=1)
    print("Got skus")

asyncio.run(main())
