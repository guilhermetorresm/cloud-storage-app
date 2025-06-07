from fastapi import APIRouter

from .health import router as health_router
from .users import router as users_router
from .auth import router as auth_router

# Router principal da API v1
api_v1_router = APIRouter(prefix="/v1")

# Incluir todos os roteadores
api_v1_router.include_router(health_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(auth_router)