import asyncio
from src.app.container import DomainsContainer
from src.foundation.logging.context import set_request_id
from src.foundation.configuration import get_settings

async def main():
    set_request_id("test")
    container = DomainsContainer()
    container.core.config.from_dict(get_settings().model_dump())
    
    print("Getting session via DI...")
    # This simulates what is passed to SKURepository
    session = container.core.db().scoped_session()
    
    print(f"Session object: {type(session)}")
    print("Executing query...")
    from sqlalchemy import text
    result = await session.execute(text("SELECT 1"))
    print(f"Result: {result.scalar()}")

asyncio.run(main())
