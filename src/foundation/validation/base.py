from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """
    Base validation schema for all DTOs and API payloads.
    Provides standard configuration like alias generation, strict types, etc.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        str_strip_whitespace=True
    )
