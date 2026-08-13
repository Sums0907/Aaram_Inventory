import re

with open("scripts/certify_bom_module.py", "r") as f:
    content = f.read()

content = content.replace(
    'cat = CategoryModel(id=uuid.uuid4(), name="TestCat", category_code="TC", parent_id=None, status="ACTIVE")',
    'cat = CategoryModel(id=uuid.uuid4(), category_name="TestCat", category_code="TC", parent_id=None, status="ACTIVE")'
)

content = content.replace('name="Dreamy-01 Fabric"', 'product_name="Dreamy-01 Fabric"')
content = content.replace('name="Sewing Thread"', 'product_name="Sewing Thread"')
content = content.replace('name="Elastic"', 'product_name="Elastic"')
content = content.replace('name="Bedsheet Packaging Bag"', 'product_name="Bedsheet Packaging Bag"')
content = content.replace('name="Blue Bay Bedsheet"', 'product_name="Blue Bay Bedsheet"')
content = content.replace('name="No BOM FG"', 'product_name="No BOM FG"')

with open("scripts/certify_bom_module.py", "w") as f:
    f.write(content)

