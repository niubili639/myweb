from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter()


@router.get("/health", summary="Health check")
def health_check(settings: Settings = Depends(get_settings)) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "status": "ok",
        "data": {
            "service": settings.project_name,
            "version": settings.version,
            "time": now,
        },
    }
