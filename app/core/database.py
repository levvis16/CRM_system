from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os

# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass

# Для SQLite (асинхронная версия)
DATABASE_URL = "sqlite+aiosqlite:///./crm.db"

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency для получения сессии БД
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессий для Dependency Injection"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Функция для создания таблиц (для асинхронного движка)
async def create_tables():
    """Создать все таблицы в БД (асинхронно)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)