from sqlalchemy.orm import Session
from app.models.chat_model import ChatHistory
from app.models.chat_session_model import ChatSession
from app.schemas import user_schema

def save_chat_history(db: Session, user: user_schema.User, session_id: str, company: str, query: str, response: str):
    chat_session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not chat_session:
        chat_session = ChatSession(
            session_id=session_id,
            user_id=user.id,
            company_name=company,
            title=query
        )
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)

    chat_history = ChatHistory(
        user_id=user.id,
        session_id=session_id,
        query=query,
        response=response
    )
    db.add(chat_history)
    db.commit()
    db.refresh(chat_history)
    return chat_history

def get_chat_history(db: Session, session_id: str):
    return db.query(ChatHistory).filter(ChatHistory.session_id == session_id).all()
