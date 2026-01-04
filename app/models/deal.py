from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship  # ← пока убрать

from app.core.database import Base

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    amount = Column(Float)
    stage = Column(String, default="lead")
    probability = Column(Integer, default=0)
    
    # Связи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    
    # Даты
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Отношения (пока закомментировать)
    # user = relationship("User", back_populates="deals")
    # contact = relationship("Contact", back_populates="deals")