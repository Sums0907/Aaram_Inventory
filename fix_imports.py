import re

def fix(file):
    with open(file, 'r') as f:
        content = f.read()
    if 'formatQuantityValue' in content and 'formatQuantityValue(' not in content:
        content = content.replace('import { formatQuantityValue } from "@/lib/utils"\n', '')
        content = content.replace(', formatQuantityValue }', ' }')
        with open(file, 'w') as f:
            f.write(content)

fix('frontend/src/pages/inventory/PhysicalVerificationPage.tsx')
fix('frontend/src/pages/inventory/GoodsReceiptsPage.tsx')
fix('frontend/src/pages/inventory/BOMSetupPage.tsx')
fix('frontend/src/pages/inventory/AdjustmentsPage.tsx')

