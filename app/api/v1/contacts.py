from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter()

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
):
    """Получить список контактов"""
    # Базовый запрос
    query = select(Contact).where(Contact.user_id == current_user.id)
    
    # Простой поиск по имени или email
    if search:
        query = query.where(
            (Contact.full_name.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%")) |
            (Contact.phone.ilike(f"%{search}%"))
        )
    
    # Пагинация
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    contacts = result.scalars().all()
    return contacts

@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact_in: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать новый контакт"""
    # Проверяем уникальность email
    if contact_in.email:
        existing = await db.execute(
            select(Contact).where(
                Contact.email == contact_in.email,
                Contact.user_id == current_user.id
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(400, "Contact with this email already exists")
    
    # Создаем контакт
    contact = Contact(**contact_in.dict(), user_id=current_user.id)
    
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    
    return contact

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить контакт по ID"""
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        )
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(404, "Contact not found")
    
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_in: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить контакт"""
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        )
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(404, "Contact not found")
    
    # Обновляем только переданные поля
    update_data = contact_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    await db.commit()
    await db.refresh(contact)
    
    return contact

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить контакт"""
    result = await db.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.user_id == current_user.id
        )
    )
    contact = result.scalar_one_or_none()
    
    if not contact:
        raise HTTPException(404, "Contact not found")
    
    await db.delete(contact)
    await db.commit()
    
    return {"message": "Contact deleted"}