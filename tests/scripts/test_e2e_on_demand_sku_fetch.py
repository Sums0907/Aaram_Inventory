import sys
import os
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Add workspaces to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../AaramPackingApp/backend")))

# Packer Imports
from app.database import Base as PackerBase, engine as packer_engine, SessionLocal as PackerSessionLocal
from app.models import PackerSkuProjection, PackerStockProjection, InventorySyncEvent
from app.inventory_event_handler import InventoryEventHandler

def run_certification():
    print("==================================================================")
    print("🚀 RUNNING E2E ON-DEMAND SKU FETCH CERTIFICATION 🚀")
    print("==================================================================")

    test_sku_id = str(uuid.uuid4())
    event_id = f"evt_stock_change_{str(uuid.uuid4())[:8]}"
    
    print("\n[1] Preparing Test Payload (STOCK_BALANCE_CHANGED for Unknown SKU)...")
    payload = {
        "inventory_sku_id": test_sku_id,
        "available_qty": 42.0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    packer_db = PackerSessionLocal()
    
    # Ensure SKU does NOT exist in Packer
    existing_sku = packer_db.query(PackerSkuProjection).filter_by(inventory_sku_id=test_sku_id).first()
    if existing_sku:
        packer_db.delete(existing_sku)
        packer_db.commit()

    print("\n[2] Mocking Inventory API Response (Simulating Network Fetch)...")
    mock_api_response = {
        "data": {
            "id": test_sku_id,
            "sku_code": "DYNAMIC-SKU-123",
            "barcode": "DYN-BAR-456",
            "status": "ACTIVE",
            "product": {
                "product_name": "On-Demand Fetched Product"
            }
        }
    }
    
    # We will patch httpx.Client.get to intercept the outbound API call from Packer
    with patch("httpx.Client.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_api_response
        mock_get.return_value = mock_resp
        
        handler = InventoryEventHandler(packer_db)
        
        print("\n[3] Triggering Packer Event Handler...")
        handler.process_event(
            event_id=event_id,
            event_type="STOCK_BALANCE_CHANGED",
            payload=payload
        )
        packer_db.commit()
        
        print("    ✅ Event processed successfully.")
        
        # Verify the mock was called exactly once
        mock_get.assert_called_once()
        print(f"    ✅ Verified synchronous API fetch executed to: {mock_get.call_args[0][0]}")

    print("\n[4] Verifying Packer Read Models...")
    # Verify Stock Projection
    stock_proj = packer_db.query(PackerStockProjection).filter_by(inventory_sku_id=test_sku_id).first()
    if not stock_proj or stock_proj.available_qty != 42.0:
        raise Exception("❌ FAILED: Stock projection was not updated correctly.")
    print("    ✅ Stock Projection verified (Qty: 42.0)")
    
    # Verify SKU Projection (The magical part)
    sku_proj = packer_db.query(PackerSkuProjection).filter_by(inventory_sku_id=test_sku_id).first()
    if not sku_proj:
        raise Exception("❌ FAILED: SKU metadata was not dynamically fetched and saved!")
    
    if sku_proj.sku_code != "DYNAMIC-SKU-123" or sku_proj.product_name != "On-Demand Fetched Product":
        raise Exception("❌ FAILED: Dynamic SKU metadata does not match expected payload!")
        
    print(f"    ✅ Dynamic SKU metadata verified (Name: '{sku_proj.product_name}', Code: '{sku_proj.sku_code}')")

    # Cleanup
    print("\n[5] Cleaning up Test Data (Raw SQL Bypassing Hooks)...")
    from sqlalchemy import text
    packer_db.execute(text(f"DELETE FROM packer_sku_projection WHERE inventory_sku_id = '{test_sku_id}'"))
    packer_db.execute(text(f"DELETE FROM packer_stock_projection WHERE inventory_sku_id = '{test_sku_id}'"))
    packer_db.execute(text(f"DELETE FROM inventory_sync_events WHERE event_id = '{event_id}'"))
    packer_db.commit()
    packer_db.close()
    
    print("    ✅ Data sanitized.")

    print("\n==================================================================")
    print("🏆 ON-DEMAND SKU FETCH CERTIFICATION PASSED 🏆")
    print("==================================================================")

if __name__ == "__main__":
    run_certification()
