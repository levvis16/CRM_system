from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.v1 import contacts, deals, tasks, analytics, integrations
from app.api import websocket
from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import create_first_superuser

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
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await create_first_superuser()
    
    logger.info("CRM application started successfully!")
    
    yield
    
    
    logger.info("Shutting down CRM application...")
    await engine.dispose()
    logger.info("CRM application shut down.")

# Создание FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Настройка CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Подключаем роутеры API v1
app.include_router(
    contacts.router,
    prefix=f"{settings.API_V1_STR}/contacts",
    tags=["contacts"],
)

'''

app.include_router(
    deals.router,
    prefix=f"{settings.API_V1_STR}/deals",
    tags=["deals"],
)

app.include_router(
    tasks.router,
    prefix=f"{settings.API_V1_STR}/tasks",
    tags=["tasks"],
)

app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_STR}/analytics",
    tags=["analytics"],
)

app.include_router(
    integrations.router,
    prefix=f"{settings.API_V1_STR}/integrations",
    tags=["integrations"],
)

# WebSocket endpoint
app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Проверка работоспособности приложения"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }

@app.get("/")
async def root():
    """Корневой endpoint с информацией о API"""
    return {
        "message": "Welcome to CRM API",
        "docs": "/docs",
        "version": settings.VERSION,
        "api_v1": settings.API_V1_STR,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

'''