import pytest
from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.models.tax_invoice import TaxInvoiceModel
from src.domains.operations.models.payment import PaymentModel
from src.domains.operations.models.settlement import SettlementModel
from src.domains.matching.models.job import MatchJobModel
from src.domains.matching.models.relationship import MatchRelationshipModel
from datetime import datetime, timezone

@pytest.fixture
async def setup_test_data(db_session: AsyncSession):
    user_id = uuid4()
    
    # Create Unmatched Order and Invoice
    order = SalesOrderModel(
        id=uuid4(),
        external_order_id="ORD-100",
        order_date=datetime.now(timezone.utc).date(),
        channel="SHOPDECK",
        status="CONFIRMED",
        customer_name="John Doe",
        customer_mobile="1234567890",
        shipping_address="123 Main St",
        shipping_pincode="123456",
        shipping_city="City",
        shipping_state="State",
        payment_method="PREPAID",
        gross_amount=100.0,
        discount_amount=0.0,
        shipping_fee=0.0,
        cod_fee=0.0,
        net_amount=110.0,
        created_by=user_id,
        updated_by=user_id
    )
    
    invoice = TaxInvoiceModel(
        id=uuid4(),
        invoice_no="INV-100",
        invoice_date=datetime.now(timezone.utc).date(),
        order_id=None,
        external_order_id="ORD-100",
        document_type="TAX_INVOICE",
        customer_state="Delhi",
        total_base_price=100.0,
        total_cgst=5.0,
        total_sgst=5.0,
        total_igst=0.0,
        total_tax=10.0,
        created_by=user_id,
        updated_by=user_id
    )
    
    # Create Unmatched Payment and Settlement
    settlement = SettlementModel(
        id=uuid4(),
        settlement_id="SET-200",
        cycle_date="2026-08-01",
        settlement_date=datetime.now(timezone.utc).date(),
        status="PROCESSED",
        gross_amount=110.0,
        fees=2.0,
        net_amount=108.0,
        utr_number="UTR-123",
        created_by=user_id,
        updated_by=user_id
    )
    
    payment = PaymentModel(
        id=uuid4(),
        transaction_id="PAY-200",
        transaction_type="payment",
        order_reference="ORD-100",
        payment_method="UPI",
        payment_captured_at=datetime.now(timezone.utc),
        external_settlement_id="SET-200",
        gross_amount=110.0,
        gateway_fee=2.0,
        net_amount=108.0,
        created_by=user_id,
        updated_by=user_id
    )

    db_session.add_all([order, invoice, settlement, payment])
    await db_session.commit()
    return {"order": order, "invoice": invoice, "settlement": settlement, "payment": payment}

@pytest.mark.asyncio
async def test_run_matching_engine(async_client: AsyncClient, setup_test_data, db_session: AsyncSession):
    response = await async_client.post("/api/v1/matching/jobs")
    assert response.status_code == 201
    
    data = response.json()["data"]
    assert data["successful_matches"] == 2
    assert data["exceptions_generated"] == 0
    
    # Verify Relationships
    job_id = data["id"]
    from sqlalchemy import select
    from uuid import UUID
    job_uuid = UUID(job_id)
    result = await db_session.execute(select(MatchRelationshipModel).where(MatchRelationshipModel.match_job_id == job_uuid))
    rels = result.scalars().all()
    assert len(rels) == 2
    
    # Verify Operations Models are Updated
    await db_session.refresh(setup_test_data["invoice"])
    assert setup_test_data["invoice"].order_id == setup_test_data["order"].id
    
    await db_session.refresh(setup_test_data["payment"])
    assert setup_test_data["payment"].settlement_id == setup_test_data["settlement"].id
