"""Settings and configuration service."""

from typing import Dict, Any, Optional
from logger_config import logger


class SettingsService:
    """Service for managing application settings."""
    
    def __init__(self, config):
        self.config = config
        self.settings = {
            "top_k": 5,
            "temperature": 0.7,
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "model_name": "mixtral-8x7b-32768",
            "max_tokens": 1000
        }
    
    async def get_settings(self) -> Dict[str, Any]:
        """Get all current settings."""
        try:
            logger.info("SETTINGS_SERVICE: Retrieving settings")
            return self.settings.copy()
        except Exception as e:
            logger.error(f"SETTINGS_SERVICE: Error retrieving settings: {e}")
            raise
    
    async def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update settings.
        
        Args:
            updates: Dictionary of settings to update
            
        Returns:
            Updated settings
        """
        try:
            logger.info(f"SETTINGS_SERVICE: Updating settings: {list(updates.keys())}")
            
            # Validate and update
            if "top_k" in updates:
                if 1 <= updates["top_k"] <= 20:
                    self.settings["top_k"] = updates["top_k"]
            
            if "temperature" in updates:
                if 0.0 <= updates["temperature"] <= 1.0:
                    self.settings["temperature"] = updates["temperature"]
            
            if "chunk_size" in updates:
                if 100 <= updates["chunk_size"] <= 2000:
                    self.settings["chunk_size"] = updates["chunk_size"]
            
            if "chunk_overlap" in updates:
                if 0 <= updates["chunk_overlap"] <= 500:
                    self.settings["chunk_overlap"] = updates["chunk_overlap"]
            
            logger.info("SETTINGS_SERVICE: Settings updated successfully")
            return self.settings.copy()
            
        except Exception as e:
            logger.error(f"SETTINGS_SERVICE: Error updating settings: {e}")
            raise
    
    async def reset_settings(self) -> Dict[str, Any]:
        """Reset settings to defaults."""
        try:
            logger.info("SETTINGS_SERVICE: Resetting settings to defaults")
            self.settings = {
                "top_k": 5,
                "temperature": 0.7,
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "model_name": "mixtral-8x7b-32768",
                "max_tokens": 1000
            }
            return self.settings.copy()
        except Exception as e:
            logger.error(f"SETTINGS_SERVICE: Error resetting settings: {e}")
            raise
