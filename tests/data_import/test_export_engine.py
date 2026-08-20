import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.sku import SKUModel
from src.foundation.enums import ItemType
from src.domains.data_ingestion.services.master_data_exporter import MasterDataExporter

@pytest.mark.asyncio
async def test_category_export_001_restore_export_excludes_roots(db_session: AsyncSession):
    """
    CATEGORY-EXPORT-001: Restore export (default) must not contain immutable root rows.
    """
    rm_root = CategoryModel(category_code="RM", category_name="Raw Materials")
    db_session.add(rm_root)
    await db_session.flush()
    rm_child = CategoryModel(category_code="RM-CHILD", category_name="RM Child", parent_id=rm_root.id)
    db_session.add(rm_child)
    await db_session.flush()

    exporter = MasterDataExporter(db_session)
    data = await exporter.export_all(documentation_mode=False)
    
    cat_codes = [row["Category Code"] for row in data["Operational_Categories"]]
    assert "RM" not in cat_codes
    assert "RM-CHILD" in cat_codes

@pytest.mark.asyncio
async def test_category_export_002_documentation_export_includes_roots(db_session: AsyncSession):
    """
    CATEGORY-EXPORT-002: Documentation export may contain root rows.
    """
    rm_root = CategoryModel(category_code="RM", category_name="Raw Materials")
    db_session.add(rm_root)
    await db_session.flush()
    rm_child = CategoryModel(category_code="RM-CHILD", category_name="RM Child", parent_id=rm_root.id)
    db_session.add(rm_child)
    await db_session.flush()

    exporter = MasterDataExporter(db_session)
    data = await exporter.export_all(documentation_mode=True)
    
    cat_codes = [row["Category Code"] for row in data["Operational_Categories"]]
    assert "RM" in cat_codes
    assert "RM-CHILD" in cat_codes
    
    # Check note
    rm_row = next(r for r in data["Operational_Categories"] if r["Category Code"] == "RM")
    assert "[ROOT" in rm_row["Export Note"]

@pytest.mark.asyncio
async def test_export_version_001_metadata_sheet_present(db_session: AsyncSession):
    """
    EXPORT-VERSION-001: Metadata sheet format version.
    """
    exporter = MasterDataExporter(db_session)
    data = await exporter.export_all()
    
    assert "Export_Metadata" in data
    metadata = data["Export_Metadata"][0]
    assert "Export Format Version" in metadata
    assert metadata["Export Format Version"] == "RM_MASTER_EXPORT_V1"

@pytest.mark.asyncio
async def test_export_boundary_001_excludes_fg_hierarchy(db_session: AsyncSession):
    """
    EXPORT-BOUNDARY-001: Verify Raw Material export excludes FG hierarchy completely.
    """
    # Create FG root and child
    fg_root = CategoryModel(category_code="FG", category_name="Finished Goods")
    db_session.add(fg_root)
    await db_session.flush()
    fg_child = CategoryModel(category_code="FG-CHILD", category_name="FG Child", parent_id=fg_root.id)
    db_session.add(fg_child)
    await db_session.flush()
    
    # Create FG Product and SKU
    fg_prod = ProductModel(product_code="FG-PROD", product_name="FG Prod", item_type=ItemType.FINISHED_GOODS, category_id=fg_child.id)
    db_session.add(fg_prod)
    await db_session.flush()
    fg_sku = SKUModel(item_code="FG-SKU", product_id=fg_prod.id)
    db_session.add(fg_sku)
    
    # Create RM root and child
    rm_root = CategoryModel(category_code="RM", category_name="Raw Materials")
    db_session.add(rm_root)
    await db_session.flush()
    rm_child = CategoryModel(category_code="RM-CHILD", category_name="RM Child", parent_id=rm_root.id)
    db_session.add(rm_child)
    await db_session.flush()
    
    # Create RM Product and SKU
    rm_prod = ProductModel(product_code="RM-PROD", product_name="RM Prod", item_type=ItemType.RAW_MATERIAL, category_id=rm_child.id)
    db_session.add(rm_prod)
    await db_session.flush()
    rm_sku = SKUModel(item_code="RM-SKU", product_id=rm_prod.id)
    db_session.add(rm_sku)
    
    await db_session.flush()
    
    exporter = MasterDataExporter(db_session)
    data = await exporter.export_all(documentation_mode=True)
    
    # Categories should not have FG
    cat_codes = [row["Category Code"] for row in data["Operational_Categories"]]
    assert "RM" in cat_codes
    assert "RM-CHILD" in cat_codes
    assert "FG" not in cat_codes
    assert "FG-CHILD" not in cat_codes
    
    # Raw materials should not have FG
    item_codes = [row["Item Code"] for row in data["Raw_Materials"]]
    assert "RM-SKU" in item_codes
    assert "FG-SKU" not in item_codes
