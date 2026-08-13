import asyncio
import uuid
from src.app.container import DomainsContainer

async def test_job_work_flow():
    container = DomainsContainer()
    container.wire(modules=[__name__])
    
    # Initialize DB (dummy SQLite in-memory or file for test)
    # We should get a session and use it directly.
    # Actually, it's easier to just assume the DB is ready because we're running it with the dev DB context?
    # No, container.core.config hasn't been set.
    from src.foundation.configuration import get_settings
    settings = get_settings()
    container.core.config.from_dict(settings.model_dump())
    
    sys_user = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    from src.domains.masters.schemas.supplier import SupplierCreate
    supplier_svc = container.masters.supplier_service()
    supplier = await supplier_svc.create(SupplierCreate(name="Test Job Worker", is_job_worker=True), sys_user)
    supplier_id = supplier.id
    
    # We can just use dummy UUIDs for items to test the Job Work Service independently
    # since we don't have FK constraints enforcing them in SQLite by default unless PRAGMA is on
    fg_sku_id = uuid.uuid4()
    rm_sku_id = uuid.uuid4()
    
    from src.domains.inventory.schemas.job_work import JobWorkOrderCreate, JobWorkIssueCreate, JobWorkReceiptCreate
    job_work_svc = container.inventory.job_work_service()
    
    # 5. Create Job Work Order
    jwo = await job_work_svc.create_jwo(JobWorkOrderCreate(
        jwo_number=f"JWO-TEST-{uuid.uuid4().hex[:4]}",
        job_worker_id=supplier_id,
        target_item_id=fg_sku_id,
        target_quantity=100
    ), sys_user)
    print("Created JWO:", jwo.id)
    
    # 6. Issue Raw Material
    issue = await job_work_svc.issue_material(JobWorkIssueCreate(
        jwo_id=jwo.id,
        item_id=rm_sku_id,
        quantity=120
    ), sys_user)
    print("Issued RM:", issue.id)
    
    # 7. Receive Finished Good
    receipt = await job_work_svc.receive_material(JobWorkReceiptCreate(
        jwo_id=jwo.id,
        item_id=fg_sku_id,
        quantity=100,
        scrap_quantity=5
    ), sys_user)
    print("Received FG:", receipt.id)
    print("All Job Work Service functions ran successfully.")

if __name__ == "__main__":
    asyncio.run(test_job_work_flow())
