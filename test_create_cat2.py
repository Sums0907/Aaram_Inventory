import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.domains.masters.repositories.category import CategoryRepository
from src.domains.masters.services.category import CategoryService
from src.domains.masters.schemas.category import CategoryCreate, CategoryResponse
from uuid import uuid4

async def test():
    engine = create_async_engine("sqlite+aiosqlite:///./test_manual.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        repo = CategoryRepository(session)
        service = CategoryService(repo)
        
        schema = CategoryCreate(
            category_name="TestCat2",
            item_type="FINISHED_GOODS",
            attributes=["Size", "Color"]
        )
        
        user_id = uuid4()
        cat = await service.create_category(schema, created_by=user_id)
        print("Created:", cat.id)
        
        # Test model validate
        resp = CategoryResponse.model_validate(cat, from_attributes=True)
        print("Serialized Attributes:", resp.attributes)

asyncio.run(test())
