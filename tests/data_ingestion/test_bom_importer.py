import pytest
import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.bom import BOMModel
from src.domains.masters.models.product import ProductModel
from src.domains.data_ingestion.services.bom_importer import BOMImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction

@pytest.fixture
async def pre_seed_skus(db_session):
    p = ProductModel(id=uuid.uuid4(), product_code="TGT", product_name="Target")
    s_tgt = SKUModel(id=uuid.uuid4(), item_code="TGT-SKU", sku_code="TGT-SKU", product_id=p.id)
    s_c1 = SKUModel(id=uuid.uuid4(), item_code="C1-SKU", sku_code="C1-SKU", product_id=p.id)
    s_c2 = SKUModel(id=uuid.uuid4(), item_code="C2-SKU", sku_code="C2-SKU", product_id=p.id)
    db_session.add_all([p, s_tgt, s_c1, s_c2])
    await db_session.flush()

@pytest.mark.asyncio
async def test_bom_importer(db_session, pre_seed_skus):
    importer = BOMImporter(db_session)
    
    # 1. Test Creation
    data = [
        {
            "BOM Number": "BOM-001",
            "BOM Name": "TGT BOM",
            "Finished SKU": "TGT-SKU",
            "Base Quantity": 1.0,
            "Component SKU": "C1-SKU",
            "Component Quantity": 2.5,
            "Wastage %": 0.0
        },
        {
            "BOM Number": "BOM-001",
            "BOM Name": "TGT BOM",
            "Finished SKU": "TGT-SKU",
            "Base Quantity": 1.0,
            "Component SKU": "C2-SKU",
            "Component Quantity": 5.0,
            "Wastage %": 0.0
        }
    ]
    
    res = await importer.import_data(data, is_dry_run=False)
    assert res.created_count == 2
    
    bom = (await db_session.execute(select(BOMModel).options(selectinload(BOMModel.items)).where(BOMModel.bom_number == "BOM-001"))).scalars().first()
    assert bom.version == 1
    assert bom.status == "ACTIVE"
    assert len(bom.items) == 2
    
    # 2. Test Exact Match (Ignore)
    res2 = await importer.import_data(data, is_dry_run=False)
    assert res2.ignored_count == 2
    assert res2.created_count == 0
    
    bom_check = (await db_session.execute(select(BOMModel).options(selectinload(BOMModel.items)).where(BOMModel.bom_number == "BOM-001", BOMModel.status == "ACTIVE"))).scalars().all()
    assert len(bom_check) == 1 # No new active versions created
    
    # 3. Test Content Change -> New Version Created
    data[0]["Component Quantity"] = 3.0 # Changed qty
    res3 = await importer.import_data(data, is_dry_run=False)
    assert res3.created_count == 2
    
    all_boms = (await db_session.execute(select(BOMModel).options(selectinload(BOMModel.items)).where(BOMModel.bom_number == "BOM-001").order_by(BOMModel.version))).scalars().all()
    assert len(all_boms) == 2
    assert all_boms[0].version == 1
    assert all_boms[0].status == "ARCHIVED"
    
    assert all_boms[1].version == 2
    assert all_boms[1].status == "ACTIVE"
    
    # 4. Test missing component sku (Abort row group)
    data.append({
        "BOM Number": "BOM-001",
        "BOM Name": "TGT BOM",
        "Finished SKU": "TGT-SKU",
        "Base Quantity": 1.0,
        "Component SKU": "MISSING-SKU",
        "Component Quantity": 5.0,
        "Wastage %": 0.0
    })
    res4 = await importer.import_data(data, is_dry_run=False)
    assert res4.failed_count == 3 # All 3 lines fail because one is bad
