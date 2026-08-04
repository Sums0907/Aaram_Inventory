from enum import Enum

class CountryCode(str, Enum):
    """ISO 3166-1 alpha-2 Country Codes."""
    IN = "IN"
    US = "US"
