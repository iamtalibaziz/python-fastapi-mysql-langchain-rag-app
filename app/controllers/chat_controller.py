from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
from app.schemas import user_schema, response_schema, chat_schema
from app.services import chat_service
from app.configs.database import get_db
from app.helpers.response_helper import success_response
from app.middleware.verify_access_token import verify_access_token
from typing import Optional
import uuid
from app.helpers.exceptions import CustomException

router = APIRouter()

@router.post("/", response_model=response_schema.SingleResponse[chat_schema.ChatResponse])
async def chat_with_llm(request: chat_schema.ChatRequest, db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    session_id = request.session_id if request.session_id else str(uuid.uuid4())
    response = await chat_service.chat_with_llm(request.query, request.company, session_id, db, current_user)
    return success_response(data=response)

@router.post("/upload-document", response_model=response_schema.SingleResponse[dict])
async def upload_document(company: str, document_url: Optional[str] = None, file: Optional[UploadFile] = File(None), db: Session = Depends(get_db), current_user: user_schema.User = Depends(verify_access_token)):
    if not document_url and not file:
        raise CustomException(message="Either document_url or file must be provided", status_code=status.HTTP_400_BAD_REQUEST)
    
    if file:
        await chat_service.process_and_store_document(file, company, db, current_user)
    else:
        # This part needs to be adapted to handle URL downloads and saving
        raise CustomException(message="URL document processing not implemented yet", status_code=status.HTTP_501_NOT_IMPLEMENTED)
        
    return success_response(data={"message": "Document processed and stored successfully"})
