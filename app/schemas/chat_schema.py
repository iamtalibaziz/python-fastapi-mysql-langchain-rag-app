from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, error_messages={"min_length": "Query cannot be empty"})
    session_id: Optional[str] = None
    company: Optional[str] = None

class UploadDocumentRequest(BaseModel):
    company: str = Field(..., min_length=1, error_messages={"min_length": "Company cannot be empty"})
    document_url: Optional[str] = Field(None)

class ChatResponse(BaseModel):
    id: int
    user_id: int
    session_id: str
    query: str
    response: str

    class Config:
        orm_mode = True
