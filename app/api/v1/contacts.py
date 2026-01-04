from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.crud.contact import contact_crud
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
):
    """Получить список контактов"""
    contacts = await contact_crud.get_multi(
        db, skip=skip, limit=limit, user_id=current_user.id, search=search
    )
    return contacts

@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact_in: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать новый контакт"""
    contact = await contact_crud.create_with_owner(
        db=db, obj_in=contact_in, user_id=current_user.id
    )
    return contact

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить контакт по ID"""
    contact = await contact_crud.get(db, id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_in: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить контакт"""
    contact = await contact_crud.get(db, id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    contact = await contact_crud.update(db, db_obj=contact, obj_in=contact_in)
    return contact

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить контакт"""
    contact = await contact_crud.get(db, id=contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await contact_crud.remove(db, id=contact_id)
    return {"message": "Contact deleted successfully"}