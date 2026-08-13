with open("scripts/certify_bom_module.py", "r") as f:
    content = f.read()

content = content.replace(
    'report_fail("Atomicity", "ValidationException", str(e), "Unexpected error")',
    'import traceback\n            report_fail("Atomicity", "ValidationException", str(e), "Unexpected error")\n            traceback.print_exc()'
)
content = content.replace(
    'report_fail("Inventory Truth", "Success", str(e), "Error checking balances")',
    'import traceback\n            report_fail("Inventory Truth", "Success", str(e), "Error checking balances")\n            traceback.print_exc()'
)

with open("scripts/certify_bom_module.py", "w") as f:
    f.write(content)
