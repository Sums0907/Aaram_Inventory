import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from src.domains.masters.models import ProductModel
from src.domains.masters.schemas.product import ProductResponse

DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        result = await session.execute(select(ProductModel))
        products = result.scalars().all()
        for p in products:
            try:
                ProductResponse.model_validate(p, from_attributes=True)
            except Exception as e:
                print(f"Error validating product: {p.product_code}")
                print(e)
                break

if __name__ == "__main__":
    asyncio.run(main())
