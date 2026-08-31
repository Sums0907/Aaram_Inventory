import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.foundation.dependency_injection.container import CoreContainer
from src.app.container import DomainsContainer
from src.domains.inventory.schemas.goods_receipt import GoodsReceiptCreate, GoodsReceiptItemCreate
from src.domains.inventory.schemas.purchase_return import PurchaseReturnCreate, PurchaseReturnItemCreate
from src.domains.inventory.schemas.enums import GoodsReceiptType
from src.domains.masters.models.sku import SKUModel
from src.domains.masters.models.product import ProductModel
from src.domains.masters.models.warehouse import WarehouseModel
from src.domains.masters.models.supplier import Supplier

@pytest_asyncio.fixture
async def setup_base_data(db_session: AsyncSession):
    product = ProductModel(id=uuid4(), product_name="Test Product", product_code=f"PROD-{uuid4().hex[:6]}")
    db_session.add(product)
    
    sku = SKUModel(id=uuid4(), item_code=f"TEST-ITEM-{uuid4()}", sku_code=f"TEST-SKU-{uuid4()}", product_id=product.id)
    db_session.add(sku)
    
    warehouse = WarehouseModel(
        id=uuid4(), 
        warehouse_code=f"WH-{uuid4()}", 
        warehouse_name="Test Warehouse", 
        address_line_1="Address 1", 
        city="City", 
        state="State", 
        pin_code="123456"
    )
    db_session.add(warehouse)
    
    supplier = Supplier(id=uuid4(), name="Test Supplier", is_job_worker=False)
    db_session.add(supplier)
    
    await db_session.commit()
    return {"sku": sku, "warehouse": warehouse, "supplier": supplier}


@pytest.mark.asyncio
async def test_grn_sequence_caller_supplied(setup_base_data):
    core = CoreContainer()
    core.config.from_dict({"DATABASE_URL": "sqlite+aiosqlite:///./test_cert_inventory.db", "DEBUG": False})
    domains = DomainsContainer(core=core)
    res = domains.init_resources()
    if res: await res
    
    orchestrator = domains.pipeline_orchestrator()
    service = domains.inventory.goods_receipt_service()
    
    custom_grn = f"CUSTOM-GRN-{uuid4().hex[:6]}"
    schema = GoodsReceiptCreate(
        grn_number=custom_grn,
        supplier_id=setup_base_data["supplier"].id,
        warehouse_id=setup_base_data["warehouse"].id,
        receipt_date=date.today(),
        receipt_type=GoodsReceiptType.RAW_MATERIAL_RECEIPT,
        items=[GoodsReceiptItemCreate(sku_id=setup_base_data["sku"].id, quantity=10)]
    )
    
    doc = await service.create(schema, uuid4())
    assert doc.grn_number == custom_grn
    await orchestrator.session.commit()


@pytest.mark.asyncio
async def test_grn_sequence_auto_generated(setup_base_data):
    core = CoreContainer()
    core.config.from_dict({"DATABASE_URL": "sqlite+aiosqlite:///./test_cert_inventory.db", "DEBUG": False})
    domains = DomainsContainer(core=core)
    res = domains.init_resources()
    if res: await res
    
    orchestrator = domains.pipeline_orchestrator()
    service = domains.inventory.goods_receipt_service()
    
    today = date.today()
    schema = GoodsReceiptCreate(
        grn_number=None,
        supplier_id=setup_base_data["supplier"].id,
        warehouse_id=setup_base_data["warehouse"].id,
        receipt_date=today,
        receipt_type=GoodsReceiptType.RAW_MATERIAL_RECEIPT,
        items=[GoodsReceiptItemCreate(sku_id=setup_base_data["sku"].id, quantity=10)]
    )
    
    doc = await service.create(schema, uuid4())
    prefix = f"GRN-{today.strftime('%d%m%y')}-"
    assert doc.grn_number.startswith(prefix)
    await orchestrator.session.commit()


@pytest.mark.asyncio
async def test_purchase_return_sequence_caller_supplied(setup_base_data):
    core = CoreContainer()
    core.config.from_dict({"DATABASE_URL": "sqlite+aiosqlite:///./test_cert_inventory.db", "DEBUG": False})
    domains = DomainsContainer(core=core)
    res = domains.init_resources()
    if res: await res
    
    orchestrator = domains.pipeline_orchestrator()
    service = domains.inventory.purchase_return_service()
    
    custom_prt = f"CUSTOM-PRT-{uuid4().hex[:6]}"
    schema = PurchaseReturnCreate(
        return_number=custom_prt,
        supplier_id=setup_base_data["supplier"].id,
        warehouse_id=setup_base_data["warehouse"].id,
        return_date=date.today(),
        items=[PurchaseReturnItemCreate(sku_id=setup_base_data["sku"].id, quantity=10)]
    )
    
    doc = await service.create(schema, uuid4())
    assert doc.return_number == custom_prt
    await orchestrator.session.commit()


@pytest.mark.asyncio
async def test_purchase_return_sequence_auto_generated(setup_base_data):
    core = CoreContainer()
    core.config.from_dict({"DATABASE_URL": "sqlite+aiosqlite:///./test_cert_inventory.db", "DEBUG": False})
    domains = DomainsContainer(core=core)
    res = domains.init_resources()
    if res: await res
    
    orchestrator = domains.pipeline_orchestrator()
    service = domains.inventory.purchase_return_service()
    
    today = date.today()
    schema = PurchaseReturnCreate(
        return_number=None,
        supplier_id=setup_base_data["supplier"].id,
        warehouse_id=setup_base_data["warehouse"].id,
        return_date=today,
        items=[PurchaseReturnItemCreate(sku_id=setup_base_data["sku"].id, quantity=10)]
    )
    
    doc = await service.create(schema, uuid4())
    prefix = f"PRT-{today.strftime('%d%m%y')}-"
    assert doc.return_number.startswith(prefix)
    await orchestrator.session.commit()
