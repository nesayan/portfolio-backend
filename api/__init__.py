"""API package with router composition."""

from fastapi import APIRouter

from api.routers import base, rag


api_router = APIRouter()
api_router.include_router(base.router)
api_router.include_router(rag.router)

__all__ = ["api_router"]



