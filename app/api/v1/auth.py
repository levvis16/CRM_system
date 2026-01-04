from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, Token

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Регистрация нового пользователя"""
    # Проверяем, есть ли уже пользователь с таким email
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(400, "User with this email already exists")
    
    # Создаем пользователя
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Создаем токен
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Вход пользователя"""
    # Находим пользователя
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(400, "Incorrect email or password")
    
    # Проверяем пароль
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(400, "Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(400, "User is not active")
    
    # Создаем токен
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}