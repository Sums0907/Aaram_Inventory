with open("scripts/certify_bom_module.py", "r") as f:
    content = f.read()

content = content.replace(
    'report_fail("Purchased Finished Goods", "Success", str(e), "Exception")',
    'import traceback\n            report_fail("Purchased Finished Goods", "Success", str(e), "Exception")\n            traceback.print_exc()'
)

with open("scripts/certify_bom_module.py", "w") as f:
    f.write(content)

