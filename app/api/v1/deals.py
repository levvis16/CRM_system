from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.deal import Deal
from app.schemas.deal import DealCreate, DealUpdate, DealResponse

router = APIRouter()

@router.get("/", response_model=List[DealResponse])
async def read_deals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Получить список сделок пользователя
    """
    result = await db.execute(
        select(Deal)
        .where(Deal.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    deals = result.scalars().all()
    return deals

@router.post("/", response_model=DealResponse)
async def create_deal(
    deal_in: DealCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать новую сделку
    """
    # Простая валидация
    if deal_in.amount and deal_in.amount < 0:
        raise HTTPException(400, "Amount cannot be negative")
    
    # Создаем сделку
    deal = Deal(**deal_in.dict(), user_id=current_user.id)
    
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    
    return deal

@router.get("/{deal_id}", response_model=DealResponse)
async def read_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить сделку по ID
    """
    result = await db.execute(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.user_id == current_user.id
        )
    )
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(404, "Deal not found")
    
    return deal

@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    deal_in: DealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить сделку
    """
    result = await db.execute(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.user_id == current_user.id
        )
    )
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(404, "Deal not found")
    
    # Обновляем только переданные поля
    update_data = deal_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)
    
    await db.commit()
    await db.refresh(deal)
    
    return deal

@router.delete("/{deal_id}")
async def delete_deal(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить сделку
    """
    result = await db.execute(
        select(Deal).where(
            Deal.id == deal_id,
            Deal.user_id == current_user.id
        )
    )
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(404, "Deal not found")
    
    await db.delete(deal)
    await db.commit()
    
    return {"message": "Deal deleted"}