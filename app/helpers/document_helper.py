from sqlalchemy.orm import Session
from app.models.document_model import Document
from app.schemas import user_schema

def save_document_to_db(db: Session, user: user_schema.User, company: str, file_name: str, file_path: str, file_type: str, file_size: int):
    """
    Saves the document record to the database.
    """
    document = Document(
        user_id=user.id,
        company_name=company,
        file_name=file_name,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
