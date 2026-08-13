import os
import glob
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # We'll just replace formatQuantityValue(...) with the proper unit_type where possible.
    # Actually, for now, let's just make sure the UI is using `sku.uom?.unit_type` instead of `short_name`.

    if filepath == "frontend/src/pages/inventory/ProductsPage.tsx":
        content = re.sub(
            r'formatQuantityValue\(count, uoms\?\.find\(u => u\.id === \(sku as any\)\.uom_id\)\?\.short_name\)',
            r'formatQuantityValue(count, uoms?.find(u => u.id === (sku as any).uom_id)?.unit_type)',
            content
        )
    
    if filepath == "frontend/src/components/suppliers/JobWorkerWorkspace.tsx":
        content = re.sub(
            r'return `\$\{sign\}\$\{formatQuantityValue\(qty, sku\)\} \$\{sku\?\.uom\?\.unit_code \|\| ""\}`',
            r'return `${sign}${formatQuantityValue(qty, sku?.uom?.unit_type)} ${sku?.uom?.unit_code || ""}`',
            content
        )
        content = re.sub(r'formatQuantityValue\(([^,]+),\s*sku\)', r'formatQuantityValue(\1, sku?.uom?.unit_type)', content)
        
    # Write back
    with open(filepath, 'w') as f:
        f.write(content)
        
process_file("frontend/src/pages/inventory/ProductsPage.tsx")
process_file("frontend/src/components/suppliers/JobWorkerWorkspace.tsx")

print("Done")
