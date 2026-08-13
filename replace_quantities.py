import os
import glob
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    original = content
    
    # Import utility if needed
    if 'formatQuantityValue' not in content and 'quantity' in content.lower():
        if 'import { cn }' in content:
            content = content.replace('import { cn } from "@/lib/utils"', 'import { cn, formatQuantityValue } from "@/lib/utils"')
        elif 'from "@/lib/utils"' in content:
            pass # We'll just append it or it might already have it
        else:
            # Add to top
            content = 'import { formatQuantityValue } from "@/lib/utils"\n' + content

    if filepath == "frontend/src/pages/inventory/InventoryDashboard.tsx":
        content = re.sub(r'\{exc.expected_quantity\}', '{formatQuantityValue(exc.expected_quantity)}', content)
        content = re.sub(r'\{exc.actual_quantity\}', '{formatQuantityValue(exc.actual_quantity)}', content)
        
    elif filepath == "frontend/src/pages/inventory/ActivityPage.tsx":
        content = re.sub(r"\{act.quantity > 0 \? '\+' : ''\}\{act.quantity\}", "{act.quantity > 0 ? '+' : ''}{formatQuantityValue(act.quantity)}", content)
        content = re.sub(r"\{selectedActivity.quantity > 0 \? '\+' : ''\}\{selectedActivity.quantity\}", "{selectedActivity.quantity > 0 ? '+' : ''}{formatQuantityValue(selectedActivity.quantity)}", content)
        
    elif filepath == "frontend/src/pages/inventory/TransformationsPage.tsx":
        content = re.sub(r'\{trans.quantity_consumed\}', '{formatQuantityValue(trans.quantity_consumed)}', content)
        content = re.sub(r'\{trans.quantity_produced\}', '{formatQuantityValue(trans.quantity_produced)}', content)
        
    elif filepath == "frontend/src/pages/inventory/ExceptionsPage.tsx":
        content = re.sub(r'\{exc.expected_quantity\}', '{formatQuantityValue(exc.expected_quantity)}', content)
        content = re.sub(r'\{exc.actual_quantity\}', '{formatQuantityValue(exc.actual_quantity)}', content)
        content = re.sub(r'\{selectedException.expected_quantity\}', '{formatQuantityValue(selectedException.expected_quantity)}', content)
        content = re.sub(r'\{selectedException.actual_quantity\}', '{formatQuantityValue(selectedException.actual_quantity)}', content)
        content = re.sub(r'\{selectedException.difference\}', '{formatQuantityValue(selectedException.difference)}', content)
        
    elif filepath == "frontend/src/components/inventory/LedgerDashboardDialog.tsx":
        content = re.sub(r"\{entry.movement.quantity > 0 \? '\+' : ''\}\{entry.movement.quantity\}", "{entry.movement.quantity > 0 ? '+' : ''}{formatQuantityValue(entry.movement.quantity)}", content)
        
    elif filepath == "frontend/src/components/inbound/GoodsReceiptDetailDialog.tsx":
        content = re.sub(r'\+\{item.quantity\}', '+{formatQuantityValue(item.quantity)}', content)
        
    elif filepath == "frontend/src/pages/inventory/ProductsPage.tsx":
        content = re.sub(r'\{getTotalStock\(sku.id\)\}', '{formatQuantityValue(getTotalStock(sku.id), sku.uom?.unit_code)}', content)
        
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, _, files in os.walk("frontend/src/pages"):
    for file in files:
        if file.endswith(".tsx"):
            process_file(os.path.join(root, file))

for root, _, files in os.walk("frontend/src/components"):
    for file in files:
        if file.endswith(".tsx") and file != "JobWorkerWorkspace.tsx":
            process_file(os.path.join(root, file))

print("Done")
