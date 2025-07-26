from pydantic import BaseModel, Field
from typing import TypeVar, Generic, List, Any

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    success: bool = Field(..., description="Indicates if the request was successful")
    data: T = Field(..., description="The response data")

class ErrorResponse(BaseModel):
    success: bool = False
    detail: str
