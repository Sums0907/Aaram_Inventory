with open("scripts/certify_bom_module.py", "r") as f:
    content = f.read()

content = content.replace('wh.id', 'wh_id')
content = content.replace('jw.id', 'jw_id')
content = content.replace('sku_fg.id', 'sku_fg_id')
content = content.replace('sku_fabric.id', 'sku_fabric_id')

with open("scripts/certify_bom_module.py", "w") as f:
    f.write(content)
