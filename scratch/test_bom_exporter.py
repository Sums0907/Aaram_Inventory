import asyncio
from src.domains.data_ingestion.services.exporters.bom_exporter import BOMExporter
from src.app.container import DomainsContainer

async def test_export():
    container = DomainsContainer()
    container.core.config.from_dict({"DATABASE_URL": "sqlite+aiosqlite:///test_create_cat.db", "DATABASE_ENV": "development"})
    
    db = container.core.db()
    async with db._session_factory() as session:
        exporter = BOMExporter(session)
        try:
            data = await exporter.export_data()
            print("Successfully exported", len(data), "BOM rows.")
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_export())
