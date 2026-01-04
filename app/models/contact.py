from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship  # ← пока убрать

from app.core.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    company = Column(String)
    position = Column(String)
    notes = Column(Text)
    
    # Связи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Даты
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения (пока закомментировать)
    # user = relationship("User", back_populates="contacts")
    # deals = relationship("Deal", back_populates="contact")