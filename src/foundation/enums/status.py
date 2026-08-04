from enum import Enum

class GenericStatus(str, Enum):
    """Standard active/inactive generic status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
