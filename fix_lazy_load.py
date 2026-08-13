with open("scripts/certify_bom_module.py", "r") as f:
    content = f.read()

# Store IDs before commit
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'await session.commit()' in line and 'sku_fabric' in content[:content.find(line)]:
        pass

content = content.replace('sku_fabric.id', 'sku_fabric_id')
content = content.replace('sku_fg.id', 'sku_fg_id')
content = content.replace('jw.id', 'jw_id')

# But we need to define sku_fabric_id = sku_fabric.id somewhere
content = content.replace(
    '        report_pass("BOM Validation")',
    '        report_pass("BOM Validation")\n        sku_fabric_id = sku_fabric.id\n        sku_fg_id = sku_fg.id\n        jw_id = jw.id'
)

with open("scripts/certify_bom_module.py", "w") as f:
    f.write(content)
