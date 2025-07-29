from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Text
from app.configs.database import Base
from sqlalchemy.orm import relationship

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    query = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User")
    session = relationship("ChatSession", back_populates="chat_history")
