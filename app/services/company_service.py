from sqlalchemy.orm import Session
from app.models.document_model import Document
from sqlalchemy import distinct

def get_all_companies(db: Session, user_id: int):
    companies = db.query(distinct(Document.company_name)).filter(Document.user_id == user_id).all()
    return [{"name": company[0]} for company in companies if company[0] is not None]
