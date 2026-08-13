import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.domains.masters.services.product import ProductService
import uuid

async def test():
    engine = create_async_engine('sqlite+aiosqlite:///test_manual.db')
    Session = async_sessionmaker(engine)
    async with Session() as session:
        service = ProductService(session)
        product_id = uuid.UUID('1f7870e4-37f3-41e9-8f80-0abab5f366bb')
        await service.delete_product(product_id)
        print("Product deleted!")

if __name__ == "__main__":
    asyncio.run(test())
