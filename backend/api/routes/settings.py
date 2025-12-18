"""Settings endpoints."""

from fastapi import APIRouter, HTTPException
from api.models.requests import SettingsRequest
from logger_config import logger

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
async def get_settings() -> dict:
    """Get current settings."""
    try:
        logger.info("ENDPOINT: /settings - Get")
        
        from main import settings_service
        
        return await settings_service.get_settings()
        
    except Exception as e:
        logger.error(f"ENDPOINT: /settings error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("")
async def update_settings(request: SettingsRequest) -> dict:
    """Update settings."""
    try:
        logger.info("ENDPOINT: /settings - Update")
        
        from main import settings_service
        
        updates = request.dict(exclude_unset=True)
        return await settings_service.update_settings(updates)
        
    except Exception as e:
        logger.error(f"ENDPOINT: /settings error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_settings() -> dict:
    """Reset settings to defaults."""
    try:
        logger.info("ENDPOINT: /settings/reset")
        
        from main import settings_service
        
        return await settings_service.reset_settings()
        
    except Exception as e:
        logger.error(f"ENDPOINT: /settings/reset error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
