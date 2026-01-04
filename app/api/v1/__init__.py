from app.api.v1.contacts import router as contacts_router
from app.api.v1.deals import router as deals_router
from app.api.v1.auth import router as auth_router

__all__ = ["contacts_router", "deals_router", "auth_router"]