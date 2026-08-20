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
