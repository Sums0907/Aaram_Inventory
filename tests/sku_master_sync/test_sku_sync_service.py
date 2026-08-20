import pytest
from sqlalchemy.orm import Session
from src.domains.sku_master_sync.sku_sync_service import SkuSyncService
from sqlalchemy.orm import selectinload

from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.foundation.enums.item_type import ItemType
from src.foundation.enums.status import GenericStatus
from src.domains.inventory.models.balance import InventoryBalanceModel
from src.domains.inventory.models.movement import InventoryMovementModel
from sqlalchemy import select

@pytest.fixture
def sync_service(db_session: Session):
    return SkuSyncService(db_session)

async def test_sku_004_new_sku_creation(sync_service, db_session):
    # SKU-004
    csv_content = """Sku Id,Product Code,Name,Selling Price,Quantity,Category Path
NEW-001,BED-NEW,New Bed,2000.00,50,
"""
    report = await sync_service.sync_catalogue(csv_content, "test.csv", run_mode="COMMITTED")
    
    assert "Created:\n1" in report
    
    sku = (await db_session.execute(select(SKUModel).options(selectinload(SKUModel.product), selectinload(SKUModel.pricing), selectinload(SKUModel.packaging)).where(SKUModel.shopdeck_sku_id == "NEW-001"))).scalar_one()
    assert sku is not None
    assert sku.product.product_code == "BED-NEW"
    assert sku.product.product_name == "New Bed"
    assert sku.pricing.selling_price == 2000.00

async def test_sku_001_and_002_and_003_updates_and_ignores(sync_service, db_session):
    # Create existing SKU
    csv_1 = """Sku Id,Product Code,Name,Selling Price,Quantity
EXIST-001,BED-EX,Exist Bed,1500.00,10
"""
    await sync_service.sync_catalogue(csv_1, "test.csv", run_mode="COMMITTED")
    
    # SKU-001: Unchanged -> IGNORE
    # SKU-002: Attribute change -> UPDATE
    # SKU-003: Product Code change -> UPDATE
    csv_2 = """Sku Id,Product Code,Name,Selling Price,Quantity
EXIST-001,BED-EX-UPDATED,Exist Bed,1600.00,10
"""
    report = await sync_service.sync_catalogue(csv_2, "test.csv", run_mode="COMMITTED")
    assert "Updated:\n1" in report
    
    sku = (await db_session.execute(select(SKUModel).options(selectinload(SKUModel.product), selectinload(SKUModel.pricing), selectinload(SKUModel.packaging)).where(SKUModel.shopdeck_sku_id == "EXIST-001"))).scalar_one()
    assert sku.product.product_code == "BED-EX-UPDATED"
    assert sku.pricing.selling_price == 1600.00
    
    # SKU-001: No change
    report_ignore = await sync_service.sync_catalogue(csv_2, "test.csv", run_mode="COMMITTED")
    assert "Ignored:\n1" in report_ignore

async def test_sku_005_and_009_inventory_isolation(sync_service, db_session):
    csv = """Sku Id,Product Code,Name,Selling Price,Quantity
INV-001,BED-INV,Inv Bed,1000.00,999
"""
    await sync_service.sync_catalogue(csv, "test.csv", run_mode="COMMITTED")
    
    # Verify no inventory movements
    movements = (await db_session.execute(select(InventoryMovementModel))).scalars().all()
    assert len(movements) == 0
    
    balances = (await db_session.execute(select(InventoryBalanceModel))).scalars().all()
    assert len(balances) == 0

async def test_sku_006_and_011_archive_and_reactivation(sync_service, db_session):
    # Snapshot 1
    csv_1 = """Sku Id,Product Code,Name,Selling Price,Quantity
ARC-001,BED-ARC,Arc Bed,100.00,10
"""
    await sync_service.sync_catalogue(csv_1, "test.csv", run_mode="COMMITTED")
    
    # Snapshot 2: SKU missing
    csv_2 = """Sku Id,Product Code,Name,Selling Price,Quantity
OTHER-001,BED-OTH,Oth Bed,100.00,10
"""
    report = await sync_service.sync_catalogue(csv_2, "test.csv", run_mode="COMMITTED")
    assert "Archived:\n1" in report
    
    sku = (await db_session.execute(select(SKUModel).options(selectinload(SKUModel.product), selectinload(SKUModel.pricing), selectinload(SKUModel.packaging)).where(SKUModel.shopdeck_sku_id == "ARC-001"))).scalar_one()
    assert sku.status == GenericStatus.INACTIVE
    
    # Snapshot 3: Reactivation (SKU-011)
    csv_3 = """Sku Id,Product Code,Name,Selling Price,Quantity
ARC-001,BED-ARC,Arc Bed,100.00,10
"""
    report_reactivate = await sync_service.sync_catalogue(csv_3, "test.csv", run_mode="COMMITTED")
    assert "Updated:\n1" in report_reactivate
    assert "INACTIVE \u2192 ACTIVE" in report_reactivate
    
    await db_session.refresh(sku)
    assert sku.status == GenericStatus.ACTIVE

async def test_sku_008_duplicate_sku_id_detection(sync_service):
    csv = """Sku Id,Product Code,Name,Selling Price,Quantity
DUP-001,BED-D1,Dup Bed,100.00,10
DUP-001,BED-D2,Dup Bed,100.00,10
"""
    report = await sync_service.sync_catalogue(csv, "test.csv", run_mode="DRY_RUN")
    assert "Failed:\n1" in report
    assert "Duplicate Sku Id" in report

async def test_sku_010_product_code_collision(sync_service):
    csv = """Sku Id,Product Code,Name,Selling Price,Quantity
COL-001,BED-COL,Col Bed,100.00,10
COL-002,BED-COL,Col Bed 2,100.00,10
"""
    report = await sync_service.sync_catalogue(csv, "test.csv", run_mode="DRY_RUN")
    assert "Failed:\n1" in report
    assert "mapped to multiple Sku Ids" in report

async def test_sku_012_idempotency(sync_service, db_session):
    csv = """Sku Id,Product Code,Name,Selling Price,Quantity
IDEM-001,BED-IDEM,Idem Bed,100.00,10
"""
    # Initial execution
    await sync_service.sync_catalogue(csv, "test.csv", run_mode="COMMITTED")
    skus_before = len((await db_session.execute(select(SKUModel).options(selectinload(SKUModel.product), selectinload(SKUModel.pricing), selectinload(SKUModel.packaging)))).scalars().all())
    
    # Second execution
    report = await sync_service.sync_catalogue(csv, "test.csv", run_mode="COMMITTED")
    assert "Created:\n0" in report
    assert "Updated:\n0" in report
    assert "Archived:\n0" in report
    assert "Ignored:\n1" in report
    
    skus_after = len((await db_session.execute(select(SKUModel).options(selectinload(SKUModel.product), selectinload(SKUModel.pricing), selectinload(SKUModel.packaging)))).scalars().all())
    assert skus_before == skus_after
