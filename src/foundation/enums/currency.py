from enum import Enum

class CurrencyCode(str, Enum):
    """ISO 4217 Currency Codes."""
    INR = "INR"
    USD = "USD"
    EUR = "EUR"
