import asyncio
from src.domains.data_ingestion.services.master_data_exporter import MasterDataExporter
from src.app.container import DomainsContainer

async def test_export():
    container = DomainsContainer()
    container.core.config.from_dict({"DATABASE_URL": "sqlite+aiosqlite:///test_create_cat.db", "DATABASE_ENV": "development"})
    
    db = container.core.db()
    async with db._session_factory() as session:
        exporter = MasterDataExporter(session)
        try:
            data = await exporter.export_all()
            print("Successfully exported all data. Sheets:", list(data.keys()))
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_export())
