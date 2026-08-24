import asyncio
import uuid
from uuid_extensions import uuid7
from src.domains.masters.schemas.category import CategoryCreate
from src.app.container import DomainsContainer

async def test_create_category():
    schema = CategoryCreate(
        category_name="Frill Taiwan Bags",
        category_code="CAT-0EDC5C",
        item_type="PACKAGING_MATERIAL",
        attributes=[]
    )
    user_uuid = uuid7()
    
    container = DomainsContainer()
    container.core.config.from_dict({"DATABASE_URL": "sqlite+aiosqlite:///test_create_cat.db", "DATABASE_ENV": "development"})
    
    # Initialize DB
    db = container.core.db()
    async with db._engine.begin() as conn:
        from src.foundation.database.session import Base
        await conn.run_sync(Base.metadata.create_all)
        
    service = container.masters.category_service()
    
    try:
        category = await service.create_category(schema, created_by=user_uuid)
        print("Successfully created category:", category.id)
        print("Category Item Type:", category.item_type)
        print("Category attributes:", category.category_attributes)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_category())
