import pytest
from sqlalchemy import select
from src.domains.masters.models.supplier import Supplier
from src.domains.data_ingestion.services.supplier_importer import SupplierImporter
from src.domains.data_ingestion.services.master_data_importer import ImportAction

@pytest.mark.asyncio
async def test_supplier_importer(db_session):
    importer = SupplierImporter(db_session)
    
    # 1. Test Creation
    data = [
        {
            "Supplier Name": "Aaram Textiles",
            "Phone Number": "9876543210",
            "GSTIN": "29ABCDE1234F1Z5",
            "Is Job Worker": "TRUE"
        }
    ]
    res = await importer.import_data(data, is_dry_run=False)
    assert res.created_count == 1
    
    supplier = (await db_session.execute(select(Supplier).where(Supplier.name == "Aaram Textiles"))).scalars().first()
    assert supplier is not None
    assert supplier.contact_number == "9876543210"
    assert supplier.is_job_worker is True
    
    # 2. Test Exact Match (Ignore)
    res2 = await importer.import_data(data, is_dry_run=False)
    assert res2.ignored_count == 1
    
    # 3. Test Partial Match (Update)
    data[0]["Email"] = "contact@aaram.in"
    res3 = await importer.import_data(data, is_dry_run=False)
    assert res3.updated_count == 1
    
    supplier_updated = (await db_session.execute(select(Supplier).where(Supplier.name == "Aaram Textiles"))).scalars().first()
    assert supplier_updated.email == "contact@aaram.in"
    
    # 4. Test Ambiguous Match (Reject)
    # We provide the exact same phone number but totally different name & GSTIN
    ambiguous_data = [
        {
            "Supplier Name": "Fake Supplier Co",
            "Phone Number": "9876543210",
            "GSTIN": "99FAKE9999F9Z9"
        }
    ]
    res4 = await importer.import_data(ambiguous_data, is_dry_run=False)
    assert res4.ambiguous_count == 1
    assert res4.created_count == 0
    
    # 5. Test Creation of another with different phone
    data2 = [
         {
            "Supplier Name": "Fake Supplier Co",
            "Phone Number": "1111111111"
        }
    ]
    res5 = await importer.import_data(data2, is_dry_run=False)
    assert res5.created_count == 1
    
    # 6. Test ID-based exact fetch
    fake_supplier = (await db_session.execute(select(Supplier).where(Supplier.name == "Fake Supplier Co"))).scalars().first()
    data_id = [
        {
            "Supplier ID": str(fake_supplier.id),
            "Supplier Name": "Renamed Supplier Co"
        }
    ]
    res6 = await importer.import_data(data_id, is_dry_run=False)
    assert res6.updated_count == 1
    fake_supplier_renamed = (await db_session.execute(select(Supplier).where(Supplier.id == fake_supplier.id))).scalars().first()
    assert fake_supplier_renamed.name == "Renamed Supplier Co"
