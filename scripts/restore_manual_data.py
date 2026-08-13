import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from src.domains.masters.models.supplier import Supplier
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.masters.models.bom import BOMModel, BOMItemModel
import uuid

DATABASE_URL = "sqlite+aiosqlite:///./test_manual.db"

async def restore():
    print("Restoring data...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        # Create UOMs
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.short_name == "pcs")
        res = await session.execute(stmt)
        uom_pcs = res.scalars().first()
        if not uom_pcs:
            uom_pcs = UnitOfMeasureModel(short_name="pcs", unit_name="Pieces", unit_code="PCS", unit_type="DECIMAL", status="ACTIVE")
            session.add(uom_pcs)
        
        stmt = select(UnitOfMeasureModel).where(UnitOfMeasureModel.short_name == "m")
        res = await session.execute(stmt)
        uom_m = res.scalars().first()
        if not uom_m:
            uom_m = UnitOfMeasureModel(short_name="m", unit_name="Meter", unit_code="M", unit_type="DECIMAL", status="ACTIVE")
            session.add(uom_m)
            
        await session.flush()

        # Check if Ashok Tailor exists
        stmt = select(Supplier).where(Supplier.name == "Ashok Tailor")
        res = await session.execute(stmt)
        ashok = res.scalars().first()
        
        if not ashok:
            print("Creating Ashok Tailor...")
            ashok = Supplier(
                name="Ashok Tailor",
                contact_number="9999999999",
                email="ashok@example.com",
                gstin="27AAAAA0000A1Z5",
                address="123 Tailor Street",
                is_job_worker=True
            )
            session.add(ashok)

        stmt = select(CategoryModel).where(CategoryModel.category_name == "Bedsheets")
        res = await session.execute(stmt)
        cat_bedsheet = res.scalars().first()
        if not cat_bedsheet:
            print("Creating Category Bedsheets...")
            cat_bedsheet = CategoryModel(category_name="Bedsheets", description="Bedsheets", category_code="BED")
            session.add(cat_bedsheet)

        await session.flush()

        # Check if Terracotta Bloom Bedsheet exists
        stmt = select(ProductModel).where(ProductModel.product_name == "Terracotta Bloom Bedsheet")
        res = await session.execute(stmt)
        terra_prod = res.scalars().first()
        
        if not terra_prod:
            print("Creating Terracotta Bloom Bedsheet...")
            terra_prod = ProductModel(
                product_code="BED-TERRA-01",
                product_name="Terracotta Bloom Bedsheet",
                description="Terracotta Bloom Bedsheet with matching pillow covers",
                category_id=cat_bedsheet.id
            )
            session.add(terra_prod)
            await session.flush()
            
            # Create SKU
            terra_sku = SKUModel(
                item_code="ITM-BED-TERRA-01",
                sku_code="SKU-BED-TERRA-01",
                product_id=terra_prod.id,
                uom_id=uom_pcs.id,
                status="ACTIVE"
            )
            session.add(terra_sku)
            await session.flush()
            
            # Find Fabric
            stmt = select(SKUModel).where(SKUModel.sku_code == "SKU-FB-TERRA")
            res = await session.execute(stmt)
            fabric_sku = res.scalars().first()
            
            if not fabric_sku:
                print("Creating Fabric for BOM...")
                fabric_prod = ProductModel(
                    product_code="FB-TERRA-01",
                    product_name="Terracotta Fabric",
                    category_id=cat_bedsheet.id
                )
                session.add(fabric_prod)
                await session.flush()
                
                fabric_sku = SKUModel(
                    item_code="ITM-FB-TERRA-01",
                    sku_code="SKU-FB-TERRA",
                    product_id=fabric_prod.id,
                    uom_id=uom_m.id,
                    status="ACTIVE"
                )
                session.add(fabric_sku)
                await session.flush()
            
            if fabric_sku:
                print("Creating BOM for Terracotta Bloom Bedsheet...")
                bom = BOMModel(
                    bom_number="BOM-BED-TERRA-01",
                    target_item_id=terra_sku.id,
                    version=1,
                    status="ACTIVE"
                )
                session.add(bom)
                await session.flush()
                
                bom_item1 = BOMItemModel(
                    bom_id=bom.id,
                    component_item_id=fabric_sku.id,
                    quantity=2.875,
                    uom_id=uom_m.id
                )
                session.add(bom_item1)
        
        await session.commit()
        print("Data restored successfully.")

if __name__ == "__main__":
    asyncio.run(restore())
