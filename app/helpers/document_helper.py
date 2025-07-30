import os
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.document_model import Document
from app.schemas import user_schema

def save_document(db: Session, user: user_schema.User, company: str, file: UploadFile):
    file_path = os.path.join("storage", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        user_id=user.id,
        company_name=company,
        file_name=file.filename,
        file_path=file_path,
        file_type=file.content_type,
        file_size=file.size
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
