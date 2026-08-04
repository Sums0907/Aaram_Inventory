from enum import Enum

class Permission(str, Enum):
    """Standard generic permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    MANAGE = "manage"
