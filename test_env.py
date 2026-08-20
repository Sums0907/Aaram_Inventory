import json
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ALLOWED_ORIGINS: list[str] = Field(default_factory=list)

import os
os.environ["ALLOWED_ORIGINS"] = '["https://inventory.aarambooks.cloud"]'
try:
    settings = Settings()
    print("Parsed list:", settings.ALLOWED_ORIGINS)
except Exception as e:
    print("Parse error:", e)

os.environ["ALLOWED_ORIGINS"] = "https://inventory.aarambooks.cloud"
try:
    settings = Settings()
    print("Parsed string:", settings.ALLOWED_ORIGINS)
except Exception as e:
    print("Parse error string:", e)
