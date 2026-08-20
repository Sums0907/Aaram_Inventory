import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.domains.sku_master_sync.sku_sync_service import SkuSyncService

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///test_inventory.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    with open("input/sku_catalogues.csv", "r", encoding="utf-8") as f:
        csv_content = f.read()
        
    async with async_session() as session:
        service = SkuSyncService(session)
        report = await service.sync_catalogue(csv_content, "sku_catalogues.csv", run_mode="DRY_RUN")
        
        with open("SHOPDECK_SKU_CATALOGUE_SYNC_REPORT.md", "w", encoding="utf-8") as out:
            out.write(report)
            
if __name__ == "__main__":
    asyncio.run(main())
