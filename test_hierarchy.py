import asyncio
from src.domains.masters.services.hierarchy import InventoryHierarchyService
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

async def test():
    engine = create_async_engine('sqlite+aiosqlite:///test_manual.db')
    Session = async_sessionmaker(engine)
    async with Session() as session:
        svc = InventoryHierarchyService(session)
        print(await svc.get_hierarchy())

if __name__ == "__main__":
    asyncio.run(test())
