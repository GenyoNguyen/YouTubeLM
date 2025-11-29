"""Health check endpoint."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "YouTubeLM API"
    }
