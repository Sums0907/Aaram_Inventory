import sys
import os

files = [
    "tests/conftest.py",
    "scripts/certify_shopdeck.py",
    "scripts/certify_inventory_truth.py",
    "scripts/certify_daily_inventory_update.py",
    "scripts/certify_bom_module.py"
]

for file in files:
    with open(file, "r") as f:
        content = f.read()
    
    if 'os.environ["DATABASE_ENV"]' not in content:
        content = 'import os\nos.environ["DATABASE_ENV"] = "test"\n' + content
        with open(file, "w") as f:
            f.write(content)
        print(f"Fixed {file}")
