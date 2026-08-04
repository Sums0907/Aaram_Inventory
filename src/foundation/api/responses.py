from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel

T = TypeVar("T")

class BaseResponse(BaseModel):
    success: bool = True
    error: Optional[Any] = None

class SuccessResponse(BaseResponse, Generic[T]):
    data: T

class PaginationMeta(BaseModel):
    total: int
    page: int
    size: int
    pages: int

class PaginatedResponse(BaseResponse, Generic[T]):
    data: List[T]
    meta: PaginationMeta
