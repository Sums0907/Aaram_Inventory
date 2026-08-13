import asyncio
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

# Models
from src.foundation.database.session import Base
from src.domains.masters.models import CategoryModel, UnitOfMeasureModel, ProductModel, SKUModel, CompanyModel, WarehouseModel
from src.domains.masters.models.supplier import Supplier
from src.domains.inventory.models.job_work import JobWorkerInventoryModel

TEST_DATABASE_URL = "sqlite+aiosqlite:///test_manual.db"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

async def restore_data():
    async with TestingSessionLocal() as session:
        # 1. Create Unit of Measure 'm' with DECIMAL if it doesn't exist
        stmt_uom = select(UnitOfMeasureModel).where(UnitOfMeasureModel.unit_code == 'm')
        uom_m = (await session.execute(stmt_uom)).scalars().first()
        if not uom_m:
            uom_m = UnitOfMeasureModel(
                id=uuid.uuid4(),
                unit_code='m',
                unit_name='Meter',
                short_name='m',
                unit_type='DECIMAL'
            )
            session.add(uom_m)
        else:
            uom_m.unit_type = 'DECIMAL'

        # 2. Create Job Worker 'Ashok Tailor'
        stmt_supplier = select(Supplier).where(Supplier.name == 'Ashok Tailor')
        ashok = (await session.execute(stmt_supplier)).scalars().first()
        if not ashok:
            ashok = Supplier(
                id=uuid.uuid4(),
                name='Ashok Tailor',
                is_job_worker=True
            )
            session.add(ashok)

        # 3. Ensure Category exists
        stmt_cat = select(CategoryModel).where(CategoryModel.category_name == 'Fabric')
        cat = (await session.execute(stmt_cat)).scalars().first()
        if not cat:
            cat = CategoryModel(id=uuid.uuid4(), category_name='Fabric', category_code='FAB')
            session.add(cat)

        # 4. Create SKUs
        skus_to_create = [
            ("Terracotta Bloom Cushion Cover Roll", "RAW_MATERIAL", uom_m.id),
            ("Terracotta Bloom Roll", "RAW_MATERIAL", uom_m.id),
            ("Terracotta Bloom Bedsheet set- with filled cushions", "FINISHED_GOODS", None)
        ]

        created_skus = {}
        for sku_name, item_type, uom_id in skus_to_create:
            stmt = select(ProductModel).where(ProductModel.product_name == sku_name)
            prod = (await session.execute(stmt)).scalars().first()
            if not prod:
                prod = ProductModel(
                    id=uuid.uuid4(),
                    product_code=f"PRD-{sku_name[:5].upper()}-{uuid.uuid4().hex[:4]}",
                    product_name=sku_name,
                    category_id=cat.id,
                    item_type=item_type
                )
                session.add(prod)
            
            stmt_sku = select(SKUModel).where(SKUModel.product_id == prod.id)
            sku = (await session.execute(stmt_sku)).scalars().first()
            if not sku:
                sku = SKUModel(
                    id=uuid.uuid4(),
                    item_code=f"SKU-{sku_name[:5].upper()}-{uuid.uuid4().hex[:4]}",
                    product_id=prod.id,
                    uom_id=uom_id
                )
                session.add(sku)
            created_skus[sku_name] = sku

        await session.commit()
        print("Restored base entities.")

        # 5. Restore Job Worker Pending Stock
        stock_data = [
            ("Terracotta Bloom Cushion Cover Roll", 37.0),
            ("Terracotta Bloom Roll", 4.0)
        ]
        
        for name, pending in stock_data:
            sku = created_skus[name]
            stmt = select(JobWorkerInventoryModel).where(
                JobWorkerInventoryModel.job_worker_id == ashok.id,
                JobWorkerInventoryModel.item_id == sku.id
            )
            inv = (await session.execute(stmt)).scalars().first()
            if not inv:
                inv = JobWorkerInventoryModel(
                    id=uuid.uuid4(),
                    job_worker_id=ashok.id,
                    item_id=sku.id,
                    issued_quantity=pending,
                    consumed_quantity=0,
                    returned_quantity=0,
                    pending_quantity=pending
                )
                session.add(inv)
        
        await session.commit()
        print("Restored Job Worker Inventory.")


if __name__ == "__main__":
    asyncio.run(restore_data())
