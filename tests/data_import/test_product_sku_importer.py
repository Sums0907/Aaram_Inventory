"""
CERT-010: SKU Identity Protection (item_code, sku_code, barcode immutable)
CERT-011: SKU Attribute Update (price, color, size updatable)
CERT-015: Dependency Order Validation (BOM SKU must exist)
"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from tests.data_import.fixtures.cert_fixtures import cert_session, seed_sku, seed_uom
from src.domains.masters.models.sku import SKUModel
from src.domains.data_ingestion.services.product_sku_importer import ProductSKUImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction


@pytest.mark.asyncio
async def test_cert010_sku_identity_protection_barcode(cert_session):
    """CERT-010: Barcode is permanently immutable — any change attempt must be REJECTED."""
    importer = ProductSKUImporter(cert_session)

    # Create
    data = [{"Item Code": "SKU-BLUE-K", "Name": "Blue King", "Barcode": "111111111111",
             "Selling Price": 499, "MRP": 999}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.created_count == 1

    # Attempt barcode change
    data[0]["Barcode"] = "999999999999"
    r2 = await importer.import_data(data, is_dry_run=False)
    assert r2.failed_count == 1, "CERT-010 FAIL: Barcode change was allowed"
    assert "immutable" in r2.row_results[0].errors[0].lower()

    # Verify barcode unchanged in DB
    sku = (await cert_session.execute(select(SKUModel).where(SKUModel.item_code == "SKU-BLUE-K"))).scalars().first()
    assert sku.barcode == "111111111111", "CERT-010 FAIL: Barcode was mutated in DB"


@pytest.mark.asyncio
async def test_cert011_sku_attribute_update(cert_session):
    """CERT-011: Price and color are mutable — partial match should update them."""
    importer = ProductSKUImporter(cert_session)

    data = [{"Item Code": "SKU-TEST", "Name": "Test Item", "Colour": "Blue",
             "Selling Price": 499, "MRP": 999}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.created_count == 1

    # Update colour and price
    data[0]["Colour"] = "Navy Blue"
    data[0]["Selling Price"] = 599
    r2 = await importer.import_data(data, is_dry_run=False)
    assert r2.updated_count == 1, "CERT-011 FAIL: Attribute update not recognised"

    sku = (await cert_session.execute(
        select(SKUModel).options(selectinload(SKUModel.pricing))
        .where(SKUModel.item_code == "SKU-TEST")
    )).scalars().first()
    assert sku.color == "Navy Blue", "CERT-011 FAIL: color not updated"
    assert float(sku.pricing.selling_price) == 599.0, "CERT-011 FAIL: price not updated"
    assert sku.item_code == "SKU-TEST", "CERT-011 FAIL: Item code was changed"
