from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from app.configs.database import Base
from sqlalchemy.orm import relationship

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_name = Column(String(255), nullable=True)
    title = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User")
    chat_history = relationship("ChatHistory", back_populates="session")
