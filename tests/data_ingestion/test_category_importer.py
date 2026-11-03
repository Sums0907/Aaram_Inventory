import pytest
import uuid
from sqlalchemy import select
from src.domains.masters.models.category import CategoryModel
from src.domains.data_ingestion.services.category_importer import CategoryImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction

@pytest.mark.asyncio
async def test_category_importer(db_session):
    importer = CategoryImporter(db_session)
    
    # Pre-seed a root category to test constraints. Uses "RM" rather than the
    # reserved "FG" root code, which CategoryOwnershipResolver treats as the
    # Finished Goods domain root and would reject any child created under it.
    root_id = uuid.uuid4()
    root_cat = CategoryModel(
        id=root_id,
        category_code="RM",
        category_name="Raw Materials"
    )
    db_session.add(root_cat)
    await db_session.flush()

    # 1. Test Root Protection (Should fail)
    data = [
        {
            "Category Code": "RM",
            "Category Name": "Modified Raw Materials"
        }
    ]
    res = await importer.import_data(data, is_dry_run=False)
    assert res.failed_count == 1

    fg_cat = (await db_session.execute(select(CategoryModel).where(CategoryModel.category_code == "RM"))).scalars().first()
    assert fg_cat.category_name == "Raw Materials" # Unchanged

    # 2. Test Creation
    data_new = [
        {
            "Category Code": "SHIRTS",
            "Category Name": "Shirts",
            "Parent Category Code": "RM"
        }
    ]
    res2 = await importer.import_data(data_new, is_dry_run=False)
    assert res2.created_count == 1
    
    new_cat = (await db_session.execute(select(CategoryModel).where(CategoryModel.category_code == "SHIRTS"))).scalars().first()
    assert new_cat.category_name == "Shirts"
    assert new_cat.parent_id == root_id
    
    # 3. Test Parent Change (Should fail)
    data_new[0]["Parent Category Code"] = "NONEXISTENT"
    res3 = await importer.import_data(data_new, is_dry_run=False)
    assert res3.failed_count == 1 # Cannot change parent
    
    # 4. Test Update
    data_update = [
        {
            "Category Code": "SHIRTS",
            "Category Name": "T-Shirts",
            "Parent Category Code": "RM"
        }
    ]
    res4 = await importer.import_data(data_update, is_dry_run=False)
    assert res4.updated_count == 1
    
    updated_cat = (await db_session.execute(select(CategoryModel).where(CategoryModel.category_code == "SHIRTS"))).scalars().first()
    assert updated_cat.category_name == "T-Shirts"
