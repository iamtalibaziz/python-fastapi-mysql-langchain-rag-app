from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.schemas import user_schema, response_schema, chat_schema
from app.services import chat_service
from app.configs.database import get_db
from app.helpers.response_helper import success_response
from app.middleware.verify_access_token import verify_access_token
from typing import Optional, List, Union
import uuid
from app.helpers.exceptions import CustomException


def get_optional_file(file: Optional[Union[UploadFile, str]] = File(None)) -> Optional[UploadFile]:
    """
    Handles cases where an empty file is sent as a string instead of a file.
    """
    if isinstance(file, str):
        return None
    return file


router = APIRouter()

@router.post("/", response_model=response_schema.SingleResponse[chat_schema.ChatResponse])
async def chat_with_llm(request: chat_schema.ChatRequest, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    session_id = request.session_id if request.session_id else str(uuid.uuid4())
    response = await chat_service.chat_with_llm(request.query, request.company, session_id, db, current_user)
    return success_response(data=response)

@router.post("/upload-document", response_model=response_schema.SingleResponse[dict])
async def upload_document(company: str = Form(...), document_url: Optional[str] = Form(None), file: Optional[UploadFile] = Depends(get_optional_file), db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    if not document_url and not file:
        raise CustomException(message="Either document_url or file must be provided", status_code=status.HTTP_400_BAD_REQUEST)
    
    if file:
        allowed_extensions = {".pdf", ".docx"}
        file_extension = "".join(file.filename.split(".")[-1:])
        if f".{file_extension.lower()}" not in allowed_extensions:
            raise CustomException(message="Only .pdf and .docx files are allowed", status_code=status.HTTP_400_BAD_REQUEST)
        await chat_service.process_and_store_document(file, company, db, current_user)
    elif document_url:
        await chat_service.process_and_store_document_from_url(document_url, company, db, current_user)
        
    return success_response(data={"message": "Document processed and stored successfully"})

@router.get("/sessions", response_model=response_schema.ListResponse[chat_schema.ChatSessionResponse])
async def get_chat_sessions(db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    sessions = chat_service.get_chat_sessions(db, current_user)
    return success_response(data=sessions)

@router.get("/sessions/{session_id}/history", response_model=response_schema.ListResponse[chat_schema.ChatResponse])
async def get_chat_history_by_session(session_id: str, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    history = chat_service.get_chat_history_by_session(db, session_id, current_user)
    return success_response(data=history)
