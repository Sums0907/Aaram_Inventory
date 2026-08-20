import pytest
import uuid
from sqlalchemy import select
from src.domains.masters.models.category import CategoryModel
from src.domains.data_ingestion.services.category_importer import CategoryImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction

@pytest.mark.asyncio
async def test_category_importer(db_session):
    importer = CategoryImporter(db_session)
    
    # Pre-seed a root category to test constraints
    root_id = uuid.uuid4()
    root_cat = CategoryModel(
        id=root_id,
        category_code="FG",
        category_name="Finished Goods"
    )
    db_session.add(root_cat)
    await db_session.flush()
    
    # 1. Test Root Protection (Should fail)
    data = [
        {
            "Category Code": "FG",
            "Category Name": "Modified Finished Goods"
        }
    ]
    res = await importer.import_data(data, is_dry_run=False)
    assert res.failed_count == 1
    
    fg_cat = (await db_session.execute(select(CategoryModel).where(CategoryModel.category_code == "FG"))).scalars().first()
    assert fg_cat.category_name == "Finished Goods" # Unchanged
    
    # 2. Test Creation
    data_new = [
        {
            "Category Code": "SHIRTS",
            "Category Name": "Shirts",
            "Parent Category Code": "FG"
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
            "Parent Category Code": "FG"
        }
    ]
    res4 = await importer.import_data(data_update, is_dry_run=False)
    assert res4.updated_count == 1
    
    updated_cat = (await db_session.execute(select(CategoryModel).where(CategoryModel.category_code == "SHIRTS"))).scalars().first()
    assert updated_cat.category_name == "T-Shirts"
