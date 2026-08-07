from typing import List
from pydantic import BaseModel
from src.domains.masters.schemas.category import CategoryResponse
from src.domains.masters.schemas.product import ProductResponse

class HierarchyResponse(BaseModel):
    categories: List[CategoryResponse]
    products: List[ProductResponse]
