import pytest
import uuid
import pandas as pd
from sqlalchemy import select
from tests.data_import.fixtures.cert_fixtures import cert_session
from tests.data_roundtrip.utils import import_from_excel, seed_fg_references
from src.domains.masters.models.category import CategoryModel
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.inventory.models.balance import InventoryBalanceModel

async def seed_roots(session):
    rm_root = CategoryModel(id=uuid.uuid4(), category_code="RM", category_name="Raw Materials")
    pkg_root = CategoryModel(id=uuid.uuid4(), category_code="PKG", category_name="Packaging")
    fg_root = CategoryModel(id=uuid.uuid4(), category_code="FG", category_name="Finished Goods")
    con_root = CategoryModel(id=uuid.uuid4(), category_code="CON", category_name="Consumables")
    ast_root = CategoryModel(id=uuid.uuid4(), category_code="AST", category_name="Assets")
    session.add_all([rm_root, pkg_root, fg_root, con_root, ast_root])
    await session.flush()

@pytest.mark.asyncio
async def test_cert022b_boundary_protection(cert_session):
    """CERT-022B: FG Boundary Protection"""
    await seed_roots(cert_session)
    import_path = "tests/data/FG_BOUNDARY_CERTIFICATION_DATA.xlsx"
    results = await import_from_excel(import_path, cert_session)
    
    if "Categories" in results:
        assert results["Categories"].created_count == 0
    if "Inventory_Items" in results:
        assert results["Inventory_Items"].created_count == 0
        
    await cert_session.flush()
    
    cats = (await cert_session.execute(select(CategoryModel))).scalars().all()
    skus = (await cert_session.execute(select(SKUModel))).scalars().all()
    
    fg_cats = [c for c in cats if c.category_code.startswith("CAT-") and c.parent_id]
    assert len(fg_cats) == 0, "FG Categories were illegally imported"
    assert len(skus) == 0, "FG SKUs were illegally imported"

@pytest.mark.asyncio
async def test_cert022c_bom_reconstruction(cert_session):
    """CERT-022C: BOM Reconstruction with minimal references"""
    await seed_roots(cert_session)
    await seed_fg_references(cert_session)

    import_path = "tests/data/RM_MASTER_CERTIFICATION_DATA.xlsx"
    results = await import_from_excel(import_path, cert_session)
    
    if "BOM" in results:
        assert results["BOM"].failed_count == 0
        assert results["BOM"].created_count > 0

@pytest.mark.asyncio
async def test_cert022d_inventory_isolation(cert_session):
    """CERT-022D: Inventory Isolation"""
    await seed_roots(cert_session)
    await seed_fg_references(cert_session)
    
    import_path = "tests/data/RM_MASTER_CERTIFICATION_DATA.xlsx"
    await import_from_excel(import_path, cert_session)
    
    movements = (await cert_session.execute(select(InventoryMovementModel))).scalars().all()
    balances = (await cert_session.execute(select(InventoryBalanceModel))).scalars().all()
    
    assert len(movements) == 0, "Inventory Movements were illegally modified"
    assert len(balances) == 0, "Inventory Balances were illegally modified"
