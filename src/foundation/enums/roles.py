from enum import Enum

class Role(str, Enum):
    """Standard application roles."""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"
