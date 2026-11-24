"""Health check endpoint."""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", summary="Service health status")
def get_health():
    """Return operational health status, API version, and environment."""
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }
