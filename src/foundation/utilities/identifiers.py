import uuid
from uuid7 import uuid7

def generate_uuid() -> str:
    """Generate a standard UUID7 string."""
    return str(uuid7())
