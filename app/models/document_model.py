from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from app.configs.database import Base
from sqlalchemy.orm import relationship

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_name = Column(String(255))
    file_name = Column(String(255))
    file_path = Column(String(255))
    file_type = Column(String(50))
    file_size = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User")
