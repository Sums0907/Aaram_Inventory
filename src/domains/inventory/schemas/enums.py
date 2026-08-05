from enum import Enum

class MovementType(str, Enum):
    OPENING_STOCK = "OPENING_STOCK"
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    RETURN = "RETURN"
    ADJUSTMENT = "ADJUSTMENT"
    QC_RELEASE = "QC_RELEASE"

class InventoryState(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNDER_INSPECTION = "UNDER_INSPECTION"
    DAMAGED = "DAMAGED"
    LOST = "LOST"

class ExceptionSource(str, Enum):
    ACCOUNTING = "ACCOUNTING"
    MARKETPLACE = "MARKETPLACE"
    PHYSICAL = "PHYSICAL"

class ExceptionStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
