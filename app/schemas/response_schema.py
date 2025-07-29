from pydantic import BaseModel
from typing import TypeVar, Generic, List

T = TypeVar('T')


class Meta(BaseModel):
    page: int
    size: int
    total_records: int
    total_pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    meta: Meta


class ListResponse(BaseModel, Generic[T]):
    success: bool
    data: List[T]

class ListWithTotalResponse(BaseModel, Generic[T]):
    success: bool
    data: List[T]
    total_records: int

class SingleResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str | None = None
    data: T | None = None

class SuccessOnlyResponse(BaseModel):
    success: bool = True

class SuccessWithIdOnlyResponse(BaseModel):
    success: bool = True
    id: int


class ErrorResponse(BaseModel):
    success: bool = False
    message: str


class ValidationErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: List[str] | None = None

