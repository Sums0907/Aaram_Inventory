"""
CERT-006: Category Root Protection
CERT-007: Category Hierarchy Validation (parent lock)
CERT-008: Category Archive Behaviour
CERT-009: Finished Goods Catalogue Governance
"""
import pytest
from sqlalchemy import select
from tests.data_import.fixtures.cert_fixtures import cert_session, seed_category
from src.domains.masters.models.category import CategoryModel
from src.domains.data_ingestion.services.category_importer import CategoryImporter, ROOT_CATEGORIES
from src.domains.data_ingestion.services.master_data_importer import ImportAction


@pytest.mark.asyncio
async def test_cert006_root_category_protection(cert_session):
    """CERT-006: Root categories (FG, RM, PKG, CON, AST) must never be renamed or modified via import."""
    importer = CategoryImporter(cert_session)

    for root_code, root_name in ROOT_CATEGORIES.items():
        # Attempt to rename each root category
        data = [{"Category Code": root_code, "Category Name": "RENAMED_ATTEMPT", "Status": "ACTIVE"}]
        r = await importer.import_data(data, is_dry_run=False)
        assert r.failed_count == 1, f"CERT-006 FAIL: Root '{root_code}' was not protected"

    # Verify none exist in DB (they were never seeded — import was blocked)
    for root_code in ROOT_CATEGORIES:
        row = (await cert_session.execute(
            select(CategoryModel).where(CategoryModel.category_code == root_code)
        )).scalars().first()
        assert row is None, f"CERT-006 FAIL: Root category '{root_code}' was written to DB"


@pytest.mark.asyncio
async def test_cert007_category_hierarchy_parent_lock(cert_session):
    """CERT-007: Once a category has a parent, the parent cannot be changed via import."""
    rm_root = CategoryModel(category_code="RM", category_name="Raw Materials")
    cert_session.add(rm_root)
    await cert_session.flush()

    parent_a = await seed_category(cert_session, "CAT-A", "Parent A", parent_id=rm_root.id)
    parent_b = await seed_category(cert_session, "CAT-B", "Parent B", parent_id=rm_root.id)
    child = await seed_category(cert_session, "CAT-CHILD", "Child", parent_id=parent_a.id)

    importer = CategoryImporter(cert_session)

    # Attempt to move child under parent_b
    data = [{"Category Code": "CAT-CHILD", "Category Name": "Child", "Parent Category Code": "CAT-B", "Status": "ACTIVE"}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.failed_count == 1, "CERT-007 FAIL: Parent change was allowed"
    assert "Cannot change parent" in r.row_results[0].errors[0]

    # Verify hierarchy unchanged
    row = (await cert_session.execute(select(CategoryModel).where(CategoryModel.category_code == "CAT-CHILD"))).scalars().first()
    assert row.parent_id == parent_a.id, "CERT-007 FAIL: Parent was changed in DB"


@pytest.mark.asyncio
async def test_cert008_category_archive_behaviour(cert_session):
    """CERT-008: A category can be archived (set INACTIVE) via import without breaking FK references."""
    cat = await seed_category(cert_session, "CAT-ACTIVE", "Active Category")

    importer = CategoryImporter(cert_session)

    # Archive it
    data = [{"Category Code": "CAT-ACTIVE", "Category Name": "Active Category", "Status": "INACTIVE"}]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.updated_count == 1, "CERT-008 FAIL: Archive update not applied"

    row = (await cert_session.execute(select(CategoryModel).where(CategoryModel.category_code == "CAT-ACTIVE"))).scalars().first()
    from src.foundation.enums.status import GenericStatus
    assert row.status == GenericStatus.INACTIVE, "CERT-008 FAIL: Category not archived"


@pytest.mark.asyncio
async def test_cert009_within_batch_hierarchy_creation(cert_session):
    """CERT-009: Within a single import file, parent categories created earlier can immediately be referenced as parents."""
    # Create RM root first
    rm_root = CategoryModel(category_code="RM", category_name="Raw Materials")
    cert_session.add(rm_root)
    await cert_session.flush()

    importer = CategoryImporter(cert_session)

    # Single batch: parent then child — child must succeed without needing a DB flush between them
    data = [
        {"Category Code": "CAT-PARENT", "Category Name": "Parent", "Parent Category Code": "RM", "Status": "ACTIVE"},
        {"Category Code": "CAT-CHILD",  "Category Name": "Child",  "Parent Category Code": "CAT-PARENT", "Status": "ACTIVE"},
    ]
    r = await importer.import_data(data, is_dry_run=False)
    assert r.failed_count == 0, f"CERT-009 FAIL: {[rr.errors for rr in r.row_results if rr.errors]}"
    assert r.created_count == 2


@pytest.mark.asyncio
async def test_cert009_reverse_order_fails(cert_session):
    """CERT-009b: If child appears before parent in the file, import should fail with a clear message."""
    importer = CategoryImporter(cert_session)

    # Reversed order — child before parent
    data = [
        {"Category Code": "CAT-CHILD",  "Category Name": "Child",  "Parent Category Code": "CAT-PARENT", "Status": "ACTIVE"},
        {"Category Code": "CAT-PARENT", "Category Name": "Parent", "Status": "ACTIVE"},
    ]
    r = await importer.import_data(data, is_dry_run=False)
    # Only the first row should fail (parent not yet known); parent row itself should succeed
    assert r.failed_count == 1
    assert "not found" in r.row_results[0].errors[0]
