import re

with open("scripts/certify_bom_module.py", "r") as f:
    content = f.read()

# Fix WarehouseModel seeding
content = content.replace(
    'wh = WarehouseModel(id=uuid.uuid4(), warehouse_code="WH-1", name="Main", type="PRIMARY", address="X", city="Y", state="Z")',
    'wh = WarehouseModel(id=uuid.uuid4(), warehouse_code="WH-1", warehouse_name="Main", description="", address_line_1="X", city="Y", state="Z", country="India", pin_code="123456")'
)

# Fix SKU seeding to not crash if prod doesn't work (well prod did work, SKU just needed error handling if exception happens)
content = content.replace("report_fail(\"Data Seeding\", \"Success\", str(e), \"Failed to seed DB\")", "report_fail(\"Data Seeding\", \"Success\", str(e), \"Failed to seed DB\")\n            raise e")

# Import all necessary repos for GoodsReceiptService
imports_to_add = """
from src.domains.inventory.repositories.movement import InventoryMovementRepository
from src.domains.inventory.repositories.balance import InventoryBalanceRepository
from src.domains.inventory.repositories.exception import InventoryExceptionRepository
from src.domains.inventory.services.balance_calculator import BalanceCalculatorService
from src.domains.inventory.services.confidence_engine import ConfidenceEngine
"""
content = content.replace("from src.domains.inventory.services.movement import InventoryMovementService", imports_to_add + "\nfrom src.domains.inventory.services.movement import InventoryMovementService")

# Instantiate correctly
instantiation = """
        mov_repo = InventoryMovementRepository(session)
        bal_repo = InventoryBalanceRepository(session)
        exc_repo = InventoryExceptionRepository(session)
        conf_engine = ConfidenceEngine(session)
        bal_calc = BalanceCalculatorService(bal_repo, mov_repo, exc_repo, conf_engine)
        movement_service = InventoryMovementService(mov_repo, bal_calc)
"""
content = content.replace("movement_service = InventoryMovementService(session)", instantiation)

with open("scripts/certify_bom_module.py", "w") as f:
    f.write(content)

