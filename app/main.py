from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Импортируем только то, что уже создали
from app.api.v1 import contacts, deals, auth
# from app.api.v1 import tasks, analytics, integrations  # ← пока не существует
# from app.api import websocket  # ← пока не существует

from app.core.database import engine, Base
# from app.core.security import create_first_superuser  # ← пока не используем

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan менеджер для управления жизненным циклом приложения
    """
    # Startup
    logger.info("Starting up CRM application...")
    
    # Создаем таблицы в БД (асинхронно)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully!")
    
    logger.info("CRM application started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CRM application...")
    await engine.dispose()  # Закрываем соединения с БД
    logger.info("CRM application shut down.")

# Создание FastAPI приложения
app = FastAPI(
    title="CRM System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для разработки можно *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем только существующие роутеры
app.include_router(
    contacts.router,
    prefix="/api/v1/contacts",
    tags=["contacts"],
)

app.include_router(
    deals.router,
    prefix="/api/v1/deals",
    tags=["deals"],
)

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["auth"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Проверка работоспособности приложения"""
    return {
        "status": "healthy",
        "service": "CRM System",
        "version": "1.0.0",
    }

@app.get("/")
async def root():
    """Корневой endpoint с информацией о API"""
    return {
        "message": "Welcome to CRM API",
        "docs": "/docs",
        "version": "1.0.0",
        "api_v1": "/api/v1",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )