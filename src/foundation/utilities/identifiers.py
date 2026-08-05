import uuid
from uuid_extensions import uuid7

def generate_uuid() -> str:
    """Generate a standard UUID7 string."""
    return str(uuid7())
