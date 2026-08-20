import pytest
from sqlalchemy import select
from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
from src.domains.data_ingestion.services.uom_importer import UOMImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction

@pytest.mark.asyncio
async def test_uom_importer(db_session):
    importer = UOMImporter(db_session)
    
    # 1. Test Creation
    data = [
        {
            "UoM Code": "KG",
            "UoM Name": "Kilogram",
            "Short Name": "kg",
            "Description": "Standard unit of mass",
            "Type": "DECIMAL",
            "Status": "ACTIVE"
        }
    ]
    
    res = await importer.import_data(data, is_dry_run=False)
    assert res.created_count == 1
    assert res.updated_count == 0
    assert res.ignored_count == 0
    assert res.failed_count == 0
    
    uom = (await db_session.execute(select(UnitOfMeasureModel).where(UnitOfMeasureModel.unit_code == "KG"))).scalars().first()
    assert uom is not None
    assert uom.unit_name == "Kilogram"
    assert uom.unit_type == "DECIMAL"
    
    # 2. Test Exact Match (Ignore)
    res = await importer.import_data(data, is_dry_run=False)
    assert res.created_count == 0
    assert res.ignored_count == 1
    
    # 3. Test Partial Match (Update)
    data[0]["Description"] = "Updated description"
    res = await importer.import_data(data, is_dry_run=False)
    assert res.updated_count == 1
    
    uom_updated = (await db_session.execute(select(UnitOfMeasureModel).where(UnitOfMeasureModel.unit_code == "KG"))).scalars().first()
    assert uom_updated.description == "Updated description"
    
    # 4. Test Missing Code (Fail)
    fail_data = [{"UoM Name": "Gram"}]
    res = await importer.import_data(fail_data, is_dry_run=False)
    assert res.failed_count == 1
