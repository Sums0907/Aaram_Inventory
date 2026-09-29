import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.domains.masters.models.sku import SKUModel
from src.domains.data_ingestion.services.product_sku_importer import ProductSKUImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction

@pytest.mark.asyncio
async def test_product_sku_importer(db_session):
    importer = ProductSKUImporter(db_session)
    
    # 1. Test Creation
    data = [
        {
            "Product Code": "TSHIRT",
            "Item Code": "TSHIRT-RED-L",
            "Sku Id": "TSHIRT-RED-L",
            "Name": "Red T-Shirt Large",
            "Selling Price": 499.0,
            "MRP": 999.0,
            "Barcode": "888123456789"
        }
    ]
    res = await importer.import_data(data, is_dry_run=False)
    assert res.created_count == 1
    
    sku = (await db_session.execute(select(SKUModel).options(selectinload(SKUModel.pricing), selectinload(SKUModel.packaging)).where(SKUModel.item_code == "TSHIRT-RED-L"))).scalars().first()
    assert sku is not None
    assert sku.barcode == "888123456789"
    assert sku.pricing.selling_price == 499.0
    
    # 2. Test Exact Match (Ignore)
    res2 = await importer.import_data(data, is_dry_run=False)
    assert res2.ignored_count == 1
    
    # 3. Test Partial Match (Update)
    data[0]["Selling Price"] = 599.0
    res3 = await importer.import_data(data, is_dry_run=False)
    assert res3.updated_count == 1
    
    sku_updated = (await db_session.execute(select(SKUModel).options(selectinload(SKUModel.pricing), selectinload(SKUModel.packaging)).where(SKUModel.item_code == "TSHIRT-RED-L"))).scalars().first()
    assert sku_updated.pricing.selling_price == 599.0
    
    # 4. Test Immutable Identity Protection (Reject)
    # Try to change barcode
    data[0]["Barcode"] = "999999999999"
    res4 = await importer.import_data(data, is_dry_run=False)
    assert res4.failed_count == 1
    assert "Cannot change immutable identity codes" in res4.row_results[0].errors[0]

@pytest.mark.asyncio
async def test_product_sku_importer_dry_run_duplicate_detection(db_session):
    importer = ProductSKUImporter(db_session)
    # Intra-file duplicate barcodes during dry-run
    data = [
        {
            "Product Code": "SHIRT-01",
            "Item Code": "SHIRT-01-S",
            "Sku Id": "SHIRT-01-S",
            "Barcode": "111222333444"
        },
        {
            "Product Code": "SHIRT-02",
            "Item Code": "SHIRT-02-M",
            "Sku Id": "SHIRT-02-M",
            "Barcode": "111222333444" # Same barcode as row 1
        }
    ]
    dry_res = await importer.import_data(data, is_dry_run=True)
    assert dry_res.created_count == 1
    assert dry_res.failed_count == 1
    assert "already exists" in dry_res.row_results[1].errors[0]

@pytest.mark.asyncio
async def test_product_sku_importer_multi_variant_same_product_code(db_session):
    importer = ProductSKUImporter(db_session)
    data = [
        {
            "Product Code": "KIDS-CANDY-SB-DB",
            "Item Code": "101SB",
            "Sku Id": "101SB",
            "Name": "Kids Candy Single Bed Sheet",
            "Barcode": "890123456001",
            "Selling Price": 499.0,
            "MRP": 999.0
        },
        {
            "Product Code": "KIDS-CANDY-SB-DB",
            "Item Code": "101SB-DB",
            "Sku Id": "101SB-DB",
            "Name": "Kids Candy Double Bed Sheet",
            "Barcode": "890123456002",
            "Selling Price": 799.0,
            "MRP": 1499.0
        }
    ]
    # 1. Dry run succeeds for both variants
    dry_res = await importer.import_data(data, is_dry_run=True)
    assert dry_res.created_count == 2
    assert dry_res.failed_count == 0

    # 2. Committed import succeeds for both variants
    commit_res = await importer.import_data(data, is_dry_run=False)
    assert commit_res.created_count == 2
    assert commit_res.failed_count == 0

    # 3. Both SKUs point to the exact same parent Product
    sku1 = (await db_session.execute(select(SKUModel).where(SKUModel.item_code == "101SB"))).scalars().first()
    sku2 = (await db_session.execute(select(SKUModel).where(SKUModel.item_code == "101SB-DB"))).scalars().first()
    assert sku1 is not None
    assert sku2 is not None
    assert sku1.shopdeck_sku_id == "101SB"
    assert sku2.shopdeck_sku_id == "101SB-DB"
    assert sku1.product_id == sku2.product_id

