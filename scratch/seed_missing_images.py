import asyncio
import csv
import uuid
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
import logging

from src.foundation.database.session import Base
from src.domains.masters.models import SKUModel, ProductImageModel

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5433/inventory_dev")
CSV_PATH = "input/sku_catalogues.csv"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        logger.info(f"Reading from {CSV_PATH}")
        
        images_added = 0
        
        with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                sku_code = row.get("Sku Id", "").strip()
                if not sku_code:
                    continue
                    
                stmt = select(SKUModel).where(SKUModel.sku_code == sku_code)
                sku = (await session.execute(stmt)).scalars().first()
                
                if not sku:
                    continue
                    
                # Images
                for i in range(1, 11):
                    img_col = f"Image {i}"
                    img_url = row.get(img_col, "").strip()
                    if img_url:
                        # Check if image already exists
                        stmt_img = select(ProductImageModel).where(
                            ProductImageModel.sku_id == sku.id,
                            ProductImageModel.image_url == img_url
                        )
                        existing_img = (await session.execute(stmt_img)).scalars().first()
                        
                        if not existing_img:
                            img = ProductImageModel(
                                id=uuid.uuid4(),
                                sku_id=sku.id,
                                image_url=img_url,
                                display_order=i
                            )
                            session.add(img)
                            images_added += 1

        await session.commit()
        logger.info(f"Successfully ingested {images_added} missing SKU images.")

if __name__ == "__main__":
    asyncio.run(main())
