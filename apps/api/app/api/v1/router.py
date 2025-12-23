from fastapi import APIRouter

from app.api.v1.endpoints import health, hello
from app.modules.auth.router import router as auth_router
from app.modules.spaces.router import router as spaces_router
from app.modules.couples.router import router as couples_router
from app.modules.media.router import router as media_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(hello.router, tags=["hello"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(spaces_router, prefix="/spaces", tags=["spaces"])
api_router.include_router(couples_router, prefix="/couples", tags=["couples"])
api_router.include_router(media_router, prefix="/media", tags=["media"])
