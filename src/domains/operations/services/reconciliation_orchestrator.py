from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from src.domains.operations.models.sales_order import SalesOrderModel, SalesOrderItemModel
from src.domains.operations.services.report_window import ShopDeckReportWindowService
from src.domains.operations.services.lifecycle_engine import LifecycleEngine, UnknownShopDeckStatusException
from src.domains.operations.schemas.lifecycle import TransitionType, ShopDeckStatus
from src.domains.inventory.services.movement import InventoryMovementService
from src.domains.inventory.schemas.movement import InventoryMovementCreate
from src.domains.inventory.models.movement import InventoryMovementModel
from src.domains.masters.models.warehouse import WarehouseModel
import os
import uuid

class ReconciliationSummary(BaseModel):
    total_rows: int = 0
    new_shopdeck_orders: int = 0
    existing_orders_processed: int = 0
    state_transitions: int = 0
    unchanged_orders: int = 0
    out_of_window_rows: int = 0
    import_exceptions: int = 0
    inventory_movements_created: int = 0

class ReconciliationOrchestratorService:
    def __init__(
        self, 
        session: AsyncSession, 
        window_service: ShopDeckReportWindowService, 
        lifecycle_engine: LifecycleEngine,
        movement_service: InventoryMovementService
    ):
        self.session = session
        self.window_service = window_service
        self.lifecycle_engine = lifecycle_engine
        self.movement_service = movement_service
        self.shopdeck_warehouse_id = None

    async def reconcile_report(
        self, 
        normalized_records: List[Dict[str, Any]], 
        uploaded_report_start_date: date, 
        uploaded_report_end_date: date,
        source_reference: Optional[str] = None
    ) -> ReconciliationSummary:
        summary = ReconciliationSummary(total_rows=len(normalized_records))
        
        # 1. Report Coverage Validation
        window_resp = await self.window_service.calculate_required_window()
        
        if window_resp.required_report_start_date and window_resp.required_report_end_date:
            if (uploaded_report_start_date > window_resp.required_report_start_date or 
                uploaded_report_end_date < window_resp.required_report_end_date):
                raise ValueError(
                    f"Report coverage insufficient. Required: {window_resp.required_report_start_date} to {window_resp.required_report_end_date}. "
                    f"Provided: {uploaded_report_start_date} to {uploaded_report_end_date}."
                )

        # Pre-fetch the configured ShopDeck warehouse
        warehouse_code = os.getenv("SHOPDECK_SALES_WAREHOUSE_CODE")
        if not warehouse_code:
            raise ValueError("SHOPDECK_SALES_WAREHOUSE_CODE environment variable is not configured.")
        
        stmt_wh = select(WarehouseModel).where(WarehouseModel.warehouse_code == warehouse_code)
        wh_res = await self.session.execute(stmt_wh)
        warehouse = wh_res.scalars().first()
        if not warehouse:
            raise ValueError(f"ShopDeck Sales Warehouse '{warehouse_code}' is not configured.")
        self.shopdeck_warehouse_id = warehouse.id

        # 2. Four-way row classification
        for record in normalized_records:
            try:
                # Basic validation (IMPORT_EXCEPTION)
                external_order_id = record.get("external_order_id")
                order_date_str = record.get("order_date")
                status = record.get("status")
                
                if not external_order_id or not order_date_str or not status:
                    summary.import_exceptions += 1
                    continue
                    
                try:
                    if isinstance(order_date_str, date):
                        order_date = order_date_str
                    else:
                        order_date = datetime.strptime(order_date_str, "%Y-%m-%d").date()
                except ValueError:
                    summary.import_exceptions += 1
                    continue

                # OUT_OF_WINDOW
                if window_resp.required_report_start_date and order_date < window_resp.required_report_start_date:
                    summary.out_of_window_rows += 1
                    continue

                # We must use nested transactions for atomicity per row
                async with self.session.begin_nested():
                    from sqlalchemy.orm import selectinload
                    stmt = select(SalesOrderModel).options(selectinload(SalesOrderModel.items)).where(SalesOrderModel.external_order_id == external_order_id)
                    res = await self.session.execute(stmt)
                    existing_order = res.scalars().first()

                    observed_at_str = record.get("observed_at")
                    if observed_at_str:
                        observed_at = datetime.fromisoformat(observed_at_str)
                    else:
                        observed_at = datetime.utcnow()

                    if existing_order:
                        # EXISTING_ORDER
                        summary.existing_orders_processed += 1
                        did_transition, _ = await self.lifecycle_engine.process_shopdeck_status_update(
                            order=existing_order,
                            new_status=status,
                            observed_at=observed_at,
                            source_reference=source_reference,
                            transition_type=TransitionType.STATE_TRANSITION.value
                        )
                        if did_transition:
                            summary.state_transitions += 1
                        else:
                            summary.unchanged_orders += 1
                    else:
                        # Temporarily set a dummy status so process_shopdeck_status_update detects a transition
                        # We use "NEW" instead of None because status is a non-nullable column and auto-flush will fail.
                        new_order = SalesOrderModel(
                            external_order_id=external_order_id,
                            channel=record.get("channel", ""),
                            order_date=order_date,
                            status="NEW", # Will be set to real status in process_shopdeck_status_update
                            customer_name=record.get("customer_name", ""),
                            customer_mobile=record.get("customer_mobile"),
                            shipping_address=record.get("shipping_address", ""),
                            shipping_pincode=record.get("shipping_pincode", ""),
                            shipping_city=record.get("shipping_city", ""),
                            shipping_state=record.get("shipping_state", ""),
                            payment_method=record.get("payment_method", ""),
                            gross_amount=record.get("gross_amount", 0.0),
                            discount_amount=record.get("discount_amount", 0.0),
                            shipping_fee=record.get("shipping_fee", 0.0),
                            cod_fee=record.get("cod_fee", 0.0),
                            net_amount=record.get("net_amount", 0.0),
                            items=[]
                        )
                        
                        from src.domains.masters.models.sku import SKUModel
                        items_data = record.get("items", [])
                        for item_data in items_data:
                            ext_sku = item_data.get("external_sku_code", "")
                            sku_obj = (await self.session.execute(select(SKUModel).where(SKUModel.sku_code == ext_sku))).scalars().first()
                            new_item = SalesOrderItemModel(
                                external_sku_code=ext_sku,
                                sku_id=sku_obj.id if sku_obj else None,
                                quantity=item_data.get("quantity", 0),
                                unit_price=item_data.get("unit_price", 0.0),
                                tax_amount=item_data.get("tax_amount", 0.0)
                            )
                            new_order.items.append(new_item)
                            
                        self.session.add(new_order)
                        await self.session.flush() # Flush to get new_order.id 

                        did_transition, _ = await self.lifecycle_engine.process_shopdeck_status_update(
                            order=new_order,
                            new_status=status,
                            observed_at=observed_at,
                            source_reference=source_reference,
                            transition_type=TransitionType.INITIAL_OBSERVATION.value
                        )
                        summary.new_shopdeck_orders += 1
                        # We don't count this as a state_transition in the summary, to keep it distinct
                        
                        existing_order = new_order
                        
                    # 3. Update Return Dates & Expectations
                    return_created_str = record.get("return_created_date")
                    return_delivered_str = record.get("return_delivered_date")
                    
                    if return_created_str:
                        existing_order.return_created_date = datetime.strptime(return_created_str, "%Y-%m-%d").date() if isinstance(return_created_str, str) else return_created_str
                        existing_order.has_open_return_expectation = True
                    if return_delivered_str:
                        existing_order.return_delivered_date = datetime.strptime(return_delivered_str, "%Y-%m-%d").date() if isinstance(return_delivered_str, str) else return_delivered_str
                        existing_order.has_open_return_expectation = False
                        
                    if status == ShopDeckStatus.RTO_INITIATED.value:
                        existing_order.has_open_rto_expectation = True
                    elif status == ShopDeckStatus.RTO_DELIVERED.value:
                        existing_order.has_open_rto_expectation = False

                    # 4. Deterministic Inventory Cycle Calculation (DISCONNECTED IN PHASE 3)
                    # ShopDeck Order Reconciliation is no longer the active source of Inventory Movements.
                    # This logic has been intentionally disconnected. Physical movements are now
                    # handled by the Packer System Integration.
                    pass

            except UnknownShopDeckStatusException:
                summary.import_exceptions += 1
            except Exception as e:
                import traceback
                traceback.print_exc()
                # Any other unexpected exception should fail this row's atomic block and log as exception
                summary.import_exceptions += 1

        return summary
