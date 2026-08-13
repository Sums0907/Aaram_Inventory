from uuid import UUID
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.domains.matching.services.engine import MatchingEngineService
from src.domains.matching.models.relationship import MatchRelationshipModel
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.domains.accounting.services.engine import AccountingEngineService
from src.domains.operations.models.sales_order import SalesOrderModel
from src.domains.operations.models.payment import PaymentModel

class PipelineOrchestratorService:
    def __init__(
        self,
        session: AsyncSession,
        matching_engine: MatchingEngineService,
        inventory_movement: InventoryMovementService,
        accounting_engine: AccountingEngineService,
        balance_calculator
    ):
        self.session = session
        self.matching_engine = matching_engine
        self.inventory_movement = inventory_movement
        self.accounting_engine = accounting_engine
        self.balance_calculator = balance_calculator

    async def run_pipeline(self, job_id: UUID, user_id: UUID):
        # 1. Run Matching
        job = await self.matching_engine.run_matching_job(job_id)
        
        # 2. Process Relationships for Inventory and Accounting
        stmt = select(MatchRelationshipModel).where(MatchRelationshipModel.match_job_id == job_id)
        result = await self.session.execute(stmt)
        relationships = result.scalars().all()
        
        processed_invoice_ids = set()
        processed_payment_ids = set()
        
        for rel in relationships:
            if rel.relationship_type == "INVOICE_TO_ORDER":
                if rel.source_id not in processed_invoice_ids:
                    await self._process_invoice_to_order(rel, user_id)
                    processed_invoice_ids.add(rel.source_id)
            elif rel.relationship_type == "PAYMENT_TO_SETTLEMENT":
                if rel.source_id not in processed_payment_ids:
                    await self._process_payment_to_settlement(rel, user_id)
                    processed_payment_ids.add(rel.source_id)
                    
        # 3. Direct Sales Order Processing (Daily Update Engine)
        # For milestones where we only import Orders and not Invoices,
        # we generate Inventory Movements directly from the Sales Order.
        await self._process_unfulfilled_sales_orders(user_id)
                
        return job

    async def _process_invoice_to_order(self, rel: MatchRelationshipModel, user_id: UUID):
        from sqlalchemy.orm import selectinload
        from src.domains.operations.models.tax_invoice import TaxInvoiceModel
        from src.domains.masters.models.sku import SKUModel
        from src.domains.masters.models.product import ProductModel
        from src.domains.masters.models.category import CategoryModel
        from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
        import uuid
        import logging
        
        # target_type is SALES_ORDER, source_type is TAX_INVOICE
        stmt_order = select(SalesOrderModel).options(selectinload(SalesOrderModel.items)).where(SalesOrderModel.id == rel.target_id)
        order = (await self.session.execute(stmt_order)).scalars().first()
        
        stmt_invoice = select(TaxInvoiceModel).where(TaxInvoiceModel.id == rel.source_id)
        invoice = (await self.session.execute(stmt_invoice)).scalars().first()
        
        if not order or not invoice:
            return
            
        # 1. Inventory Movements
        # Using negative for INVOICE, positive for CREDIT (returns)
        qty_multiplier = -1 if "INVOICE" in invoice.document_type.upper() else 1
        
        for item in order.items:
            # Auto-resolve or create SKU
            if not item.sku_id:
                stmt_sku = select(SKUModel).where(SKUModel.sku_code == item.external_sku_code)
                sku = (await self.session.execute(stmt_sku)).scalars().first()
                if not sku:
                    # For RC1, auto-create a skeleton SKU and Product
                    # Find default category and UOM
                    cat = (await self.session.execute(select(CategoryModel))).scalars().first()
                    uom = (await self.session.execute(select(UnitOfMeasureModel))).scalars().first()
                    if not cat or not uom:
                        logging.error("Missing default Category or UOM. Cannot auto-create SKU.")
                        continue
                        
                    product = ProductModel(
                        id=uuid.uuid4(),
                        product_code=f"AUTO-{item.external_sku_code}",
                        product_name=item.external_sku_code,
                        category_id=cat.id
                    )
                    self.session.add(product)
                    
                    sku = SKUModel(
                        id=uuid.uuid4(),
                        sku_code=item.external_sku_code,
                        item_code=item.external_sku_code,
                        product_id=product.id,
                        uom_id=uom.id
                    )
                    self.session.add(sku)
                    await self.session.commit()
                    await self.session.refresh(sku)
                
                item.sku_id = sku.id
                await self.session.commit()

            if item.sku_id:
                # We need a warehouse. Assuming a default warehouse exists and its ID is user_id or we fetch it.
                from src.domains.masters.models.warehouse import WarehouseModel
                wh = (await self.session.execute(select(WarehouseModel))).scalars().first()
                warehouse_id = wh.id if wh else user_id
                
                movement = InventoryMovementCreate(
                    movement_number=f"MOV-{order.external_order_id}-{item.id}",
                    movement_type="SALES_FULFILLMENT" if qty_multiplier == -1 else "CUSTOMER_RETURN",
                    movement_date=order.order_date,
                    posting_date=date.today(),
                    status="POSTED",
                    warehouse_id=warehouse_id,
                    sku_id=item.sku_id,
                    quantity=item.quantity * qty_multiplier,
                    unit_cost=item.unit_price,
                    reference_type="TAX_INVOICE",
                    reference_number=invoice.invoice_no,
                    reference_id=invoice.id
                )
                try:
                    await self.inventory_movement.create_movement(movement, user_id)
                    # Trigger Balance Recalculation!
                    await self.balance_calculator.recalculate_balance(warehouse_id, item.sku_id)
                except Exception as e:
                    logging.error(f"Failed to create movement for item {item.id}: {e}")

        # 2. Accounting Journal
        is_online = order.payment_method.upper() == "ONLINE"
        gross_amt = float(invoice.total_base_price + invoice.total_tax)
        
        amounts = {
            "online_receivable": abs(gross_amt) if is_online else 0.0,
            "cod_receivable": abs(gross_amt) if not is_online else 0.0,
            "base_price": abs(float(invoice.total_base_price)),
            "cgst": abs(float(invoice.total_cgst)),
            "sgst": abs(float(invoice.total_sgst)),
            "igst": abs(float(invoice.total_igst))
        }
        
        event_type = "SALES_FULFILLMENT" if "INVOICE" in invoice.document_type.upper() else "CUSTOMER_RETURN"
        
        await self.accounting_engine.generate_journal(
            event_type=event_type,
            reference_type="TAX_INVOICE",
            reference_number=invoice.invoice_no,
            reference_id=invoice.id,
            posting_date=date.today(),
            amounts=amounts,
            user_id=user_id
        )

    async def _process_payment_to_settlement(self, rel: MatchRelationshipModel, user_id: UUID):
        from src.domains.operations.models.settlement import SettlementModel
        
        # source_type is PAYMENT, target_type is SETTLEMENT
        stmt = select(PaymentModel).where(PaymentModel.id == rel.source_id)
        payment = (await self.session.execute(stmt)).scalars().first()
        
        stmt_settle = select(SettlementModel).where(SettlementModel.id == rel.target_id)
        settlement = (await self.session.execute(stmt_settle)).scalars().first()
        
        if not payment or not settlement:
            return
            
        is_online = settlement.bank_account and settlement.bank_account.upper() == "RAZORPAY"
        
        # We only generate settlements for PAYMENT, ignoring REFUND entities in Razorpay
        if is_online and payment.transaction_type.lower() != "payment":
            return
            
        # Authoritative external financial data always takes precedence
        cgst_val = 0.0
        sgst_val = 0.0
        if is_online:
            has_tax = hasattr(payment, "gateway_tax")
            tax_val = getattr(payment, "gateway_tax", None)
            
            # Since we added gateway_tax to the model, we should use it unconditionally for new records.
            # If we needed strict backward compatibility, we would check if tax_val is None, 
            # but since server_default=0.00, we'll just trust the DB value.
            if has_tax and tax_val is not None:
                cgst_val = float(tax_val) / 2.0
                sgst_val = float(tax_val) / 2.0
            else:
                cgst_val = float(payment.gateway_fee) * 0.18 / 2.0
                sgst_val = float(payment.gateway_fee) * 0.18 / 2.0
            
        amounts = {
            "bank_amount": float(payment.net_amount) if is_online else float(payment.gross_amount),
            "gateway_fee": float(payment.gateway_fee) if is_online else 0.0,
            "input_cgst": cgst_val,
            "input_sgst": sgst_val,
            "online_settled": float(payment.gross_amount) if is_online else 0.0,
            "cod_settled": float(payment.gross_amount) if not is_online else 0.0
        }
        
        await self.accounting_engine.generate_journal(
            event_type="SETTLEMENT_RECEIVED",
            reference_type="PAYMENT",
            reference_number=payment.transaction_id,
            reference_id=payment.id,
            posting_date=date.today(),
            amounts=amounts,
            user_id=user_id
        )

    async def _process_unfulfilled_sales_orders(self, user_id: UUID):
        from sqlalchemy.orm import selectinload
        from src.domains.masters.models.sku import SKUModel
        from src.domains.inventory.models.movement import InventoryMovementModel
        from src.domains.masters.models.warehouse import WarehouseModel
        import uuid
        import logging
        
        # Find all Sales Orders where there is NO InventoryMovement with reference_id = order.id
        stmt = (
            select(SalesOrderModel)
            .options(selectinload(SalesOrderModel.items))
            .outerjoin(InventoryMovementModel, InventoryMovementModel.reference_id == SalesOrderModel.id)
            .where(InventoryMovementModel.id.is_(None))
        )
        
        unfulfilled_orders = (await self.session.execute(stmt)).scalars().all()
        
        wh = (await self.session.execute(select(WarehouseModel))).scalars().first()
        warehouse_id = wh.id if wh else user_id
        
        for order in unfulfilled_orders:
            # We only generate movements for specific terminal statuses
            status = str(order.status).upper()
            if "DELIVERED" not in status and "RETURN" not in status and "RTO" not in status:
                continue
                
            qty_multiplier = -1 if "DELIVERED" in status else 1
            movement_type = "SALES_FULFILLMENT" if qty_multiplier == -1 else "CUSTOMER_RETURN"
            
            for item in order.items:
                if not item.sku_id:
                    # Auto-resolve or create SKU if missing
                    stmt_sku = select(SKUModel).where(SKUModel.sku_code == item.external_sku_code)
                    sku = (await self.session.execute(stmt_sku)).scalars().first()
                    if not sku:
                        from src.domains.masters.models.category import CategoryModel
                        from src.domains.masters.models.unit_of_measure import UnitOfMeasureModel
                        from src.domains.masters.models.product import ProductModel
                        
                        cat = (await self.session.execute(select(CategoryModel))).scalars().first()
                        uom = (await self.session.execute(select(UnitOfMeasureModel))).scalars().first()
                        if cat and uom:
                            product = ProductModel(
                                id=uuid.uuid4(),
                                product_code=f"AUTO-{item.external_sku_code}",
                                product_name=item.external_sku_code,
                                category_id=cat.id
                            )
                            self.session.add(product)
                            
                            sku = SKUModel(
                                id=uuid.uuid4(),
                                sku_code=item.external_sku_code,
                                item_code=item.external_sku_code,
                                product_id=product.id,
                                uom_id=uom.id
                            )
                            self.session.add(sku)
                            await self.session.commit()
                            await self.session.refresh(sku)
                            
                    if sku:
                        item.sku_id = sku.id
                        await self.session.commit()
                
                if item.sku_id:
                    movement = InventoryMovementCreate(
                        movement_number=f"MOV-{order.external_order_id}-{item.id}",
                        movement_type=movement_type,
                        movement_date=order.order_date,
                        posting_date=date.today(),
                        status="POSTED",
                        warehouse_id=warehouse_id,
                        sku_id=item.sku_id,
                        quantity=item.quantity * qty_multiplier,
                        unit_cost=item.unit_price,
                        reference_type="SALES_ORDER",
                        reference_number=order.external_order_id,
                        reference_id=order.id
                    )
                    try:
                        await self.inventory_movement.create_movement(movement, user_id)
                        await self.balance_calculator.recalculate_balance(warehouse_id, item.sku_id)
                    except Exception as e:
                        logging.error(f"Failed to create movement for order {order.id}: {e}")
