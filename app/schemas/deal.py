from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class DealBase(BaseModel):
    title: str
    description: Optional[str] = None
    amount: Optional[float] = None
    stage: str = "lead"
    probability: int = 0
    contact_id: Optional[int] = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    contact_id: Optional[int] = None


class DealResponse(DealBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True