import asyncio
import csv
import uuid
import math
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
import logging

from src.foundation.database.session import Base
from src.domains.masters.models import (
    ProductModel, SKUModel, PricingModel, PackagingModel, ProductImageModel, CategoryModel
)
from src.domains.inventory.models.movement import InventoryMovementModel

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test_manual.db")
CSV_PATH = "input/sku_catalogues.csv"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_float(val, default=0.0):
    try:
        if not val:
            return default
        f = float(val)
        if math.isnan(f):
            return default
        return f
    except ValueError:
        return default

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        # Check if default category exists
        stmt = select(CategoryModel).where(CategoryModel.category_code == "GEN")
        default_cat = (await session.execute(stmt)).scalars().first()
        if not default_cat:
            default_cat = CategoryModel(
                id=uuid.uuid4(),
                category_code="GEN",
                category_name="General"
            )
            session.add(default_cat)
            await session.commit()
            
        logger.info(f"Reading from {CSV_PATH}")
        
        products_map = {} # product_code -> ProductModel
        
        with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                product_code = row.get("Product Code", "").strip()
                if not product_code:
                    continue
                    
                # 1. Product
                if product_code not in products_map:
                    product = ProductModel(
                        id=uuid.uuid4(),
                        product_code=product_code,
                        product_name=row.get("Name", "Unknown"),
                        description=row.get("Description", ""),
                        brand=row.get("attr_Brand", ""),
                        product_type=row.get("Product Type", ""),
                        category_id=default_cat.id
                    )
                    session.add(product)
                    products_map[product_code] = product
                else:
                    product = products_map[product_code]
                    
                # 2. SKU
                sku_code = row.get("Sku Id", "").strip()
                if not sku_code:
                    continue
                    
                asin = row.get("Amazon ASIN", "").strip()
                barcode = asin if asin else None
                
                # Check if SKU already exists
                stmt = select(SKUModel).where(SKUModel.sku_code == sku_code)
                existing_sku = (await session.execute(stmt)).scalars().first()
                if existing_sku:
                    sku = existing_sku
                else:
                    sku = SKUModel(
                        id=uuid.uuid4(),
                        sku_code=sku_code,
                        product_id=product.id,
                        size=row.get("Size", ""),
                        color=row.get("Colour", ""),
                        pattern=row.get("attr_Pattern", ""),
                        material=row.get("attr_Material", ""),
                        thread_count=row.get("attr_Thread Count (TC)", ""),
                        barcode=barcode
                    )
                    session.add(sku)
                    await session.flush()
                
                # 3. Pricing
                pricing = PricingModel(
                    id=uuid.uuid4(),
                    sku_id=sku.id,
                    selling_price=safe_float(row.get("Selling Price")),
                    mrp=safe_float(row.get("MRP")),
                    cost_price=safe_float(row.get("Cost Price")),
                    gst_percentage=safe_float(row.get("GST %")),
                    hsn_code=row.get("HSN Code", "")
                )
                session.add(pricing)
                
                # 4. Packaging
                packaging = PackagingModel(
                    id=uuid.uuid4(),
                    sku_id=sku.id,
                    length=safe_float(row.get("Packaging Length (in cm)")),
                    breadth=safe_float(row.get("Packaging Breadth (in cm)")),
                    height=safe_float(row.get("Packaging Height (in cm)")),
                    weight=safe_float(row.get("Packaging Weight (in kg)")),
                    package_contents=row.get("attr_Package Contents", "")
                )
                session.add(packaging)
                
                # 5. Images
                for i in range(1, 11):
                    img_col = f"Image {i}"
                    img_url = row.get(img_col, "").strip()
                    if img_url:
                        img = ProductImageModel(
                            id=uuid.uuid4(),
                            sku_id=sku.id,
                            image_url=img_url,
                            display_order=i
                        )
                        session.add(img)

        await session.commit()
        
        # Verify
        result = await session.execute(select(SKUModel))
        skus = result.scalars().all()
        logger.info(f"Successfully ingested {len(skus)} SKUs across {len(products_map)} Products.")

if __name__ == "__main__":
    asyncio.run(main())
