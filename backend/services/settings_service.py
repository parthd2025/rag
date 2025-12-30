"""Settings and configuration service."""

from typing import Dict, Any, Optional
from ..logger_config import logger


class SettingsService:
    """Service for managing application settings."""

    def __init__(self, config, ingestor: Optional[Any] = None, rag_engine: Optional[Any] = None):
        self.config = config
        self.ingestor = ingestor
        self.rag_engine = rag_engine
        self.settings = {
            "top_k": config.TOP_K,
            "temperature": config.TEMPERATURE,
            "chunk_size": config.CHUNK_SIZE,
            "chunk_overlap": config.CHUNK_OVERLAP,
            "chunking_level": config.CHUNKING_LEVEL,
            "context_window_size": config.CONTEXT_WINDOW_SIZE,
            "max_questions_single": config.MAX_SUGGESTED_QUESTIONS_SINGLE,
            "max_questions_multi": config.MAX_SUGGESTED_QUESTIONS_MULTI,
            "model_name": config.LLM_MODEL,
            "max_tokens": config.MAX_TOKENS,
        }
        self._sync_component_state()

    def attach_components(self, ingestor: Optional[Any] = None, rag_engine: Optional[Any] = None) -> None:
        """Attach runtime components after initialization."""
        if ingestor:
            self.ingestor = ingestor
        if rag_engine:
            self.rag_engine = rag_engine
        self._sync_component_state()

    def _sync_component_state(self) -> None:
        if self.ingestor:
            self.settings["chunk_size"] = getattr(self.ingestor, "chunk_size", self.settings["chunk_size"])
            self.settings["chunk_overlap"] = getattr(self.ingestor, "chunk_overlap", self.settings["chunk_overlap"])
            level = getattr(self.ingestor, "chunking_level", None)
            if level:
                self.settings["chunking_level"] = level
        if self.rag_engine:
            self.settings["top_k"] = getattr(self.rag_engine, "top_k", self.settings["top_k"])
            self.settings["temperature"] = getattr(self.rag_engine, "temperature", self.settings["temperature"])
            window = getattr(self.rag_engine, "context_window_size", None)
            if window:
                self.settings["context_window_size"] = window

    async def get_settings(self) -> Dict[str, Any]:
        """Get all current settings."""
        try:
            logger.info("SETTINGS_SERVICE: Retrieving settings")
            self._sync_component_state()
            return self.settings.copy()
        except Exception as e:
            logger.error(f"SETTINGS_SERVICE: Error retrieving settings: {e}")
            raise

    async def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update runtime settings and propagate to components."""
        try:
            if not updates:
                return self.settings.copy()

            logger.info(f"SETTINGS_SERVICE: Updating settings: {list(updates.keys())}")

            if "top_k" in updates:
                top_k = int(updates["top_k"])
                if not 1 <= top_k <= 20:
                    raise ValueError("top_k must be between 1 and 20")
                self.settings["top_k"] = top_k
                if self.rag_engine:
                    self.rag_engine.set_top_k(top_k)

            if "temperature" in updates:
                temperature = float(updates["temperature"])
                if not 0.0 <= temperature <= 2.0:
                    raise ValueError("temperature must be between 0.0 and 2.0")
                self.settings["temperature"] = temperature
                if self.rag_engine:
                    self.rag_engine.set_temperature(temperature)

            if "chunking_level" in updates:
                level = int(updates["chunking_level"])
                if not 1 <= level <= 10:
                    raise ValueError("chunking_level must be between 1 and 10")
                self.settings["chunking_level"] = level
                if self.ingestor:
                    self.ingestor.set_chunking_level(level)

            if "chunk_size" in updates:
                chunk_size = int(updates["chunk_size"])
                if not 100 <= chunk_size <= 4000:
                    raise ValueError("chunk_size must be between 100 and 4000")
                if self.ingestor and chunk_size <= getattr(self.ingestor, "chunk_overlap", 0):
                    raise ValueError("chunk_size must be greater than current chunk_overlap")
                self.settings["chunk_size"] = chunk_size
                if self.ingestor:
                    self.ingestor.chunk_size = chunk_size

            if "chunk_overlap" in updates:
                chunk_overlap = int(updates["chunk_overlap"])
                target_chunk_size = self.settings.get("chunk_size", self.config.CHUNK_SIZE)
                if self.ingestor:
                    target_chunk_size = getattr(self.ingestor, "chunk_size", target_chunk_size)
                if not 0 <= chunk_overlap < target_chunk_size:
                    raise ValueError("chunk_overlap must be between 0 and chunk_size - 1")
                self.settings["chunk_overlap"] = chunk_overlap
                if self.ingestor:
                    self.ingestor.chunk_overlap = chunk_overlap

            if "context_window_size" in updates:
                context_window_size = int(updates["context_window_size"])
                if not 256 <= context_window_size <= 8192:
                    raise ValueError("context_window_size must be between 256 and 8192")
                self.settings["context_window_size"] = context_window_size
                if self.rag_engine and hasattr(self.rag_engine, "set_context_window_size"):
                    self.rag_engine.set_context_window_size(context_window_size)

            if "max_questions_single" in updates:
                value = int(updates["max_questions_single"])
                if not 1 <= value <= 50:
                    raise ValueError("max_questions_single must be between 1 and 50")
                self.settings["max_questions_single"] = value

            if "max_questions_multi" in updates:
                value = int(updates["max_questions_multi"])
                if not 1 <= value <= 50:
                    raise ValueError("max_questions_multi must be between 1 and 50")
                self.settings["max_questions_multi"] = value

            self._sync_component_state()
            logger.info("SETTINGS_SERVICE: Settings updated successfully")
            return self.settings.copy()

        except Exception as e:
            logger.error(f"SETTINGS_SERVICE: Error updating settings: {e}")
            raise

    async def reset_settings(self) -> Dict[str, Any]:
        """Reset settings to defaults and propagate to components."""
        try:
            logger.info("SETTINGS_SERVICE: Resetting settings to defaults")
            self.settings.update({
                "top_k": self.config.TOP_K,
                "temperature": self.config.TEMPERATURE,
                "chunk_size": self.config.CHUNK_SIZE,
                "chunk_overlap": self.config.CHUNK_OVERLAP,
                "chunking_level": self.config.CHUNKING_LEVEL,
                "context_window_size": self.config.CONTEXT_WINDOW_SIZE,
                "max_questions_single": self.config.MAX_SUGGESTED_QUESTIONS_SINGLE,
                "max_questions_multi": self.config.MAX_SUGGESTED_QUESTIONS_MULTI,
                "model_name": self.config.LLM_MODEL,
                "max_tokens": self.config.MAX_TOKENS,
            })

            if self.ingestor:
                self.ingestor.chunk_size = self.config.CHUNK_SIZE
                self.ingestor.chunk_overlap = self.config.CHUNK_OVERLAP
                self.ingestor.set_chunking_level(self.config.CHUNKING_LEVEL)

            if self.rag_engine:
                self.rag_engine.set_top_k(self.config.TOP_K)
                self.rag_engine.set_temperature(self.config.TEMPERATURE)
                if hasattr(self.rag_engine, "set_context_window_size"):
                    self.rag_engine.set_context_window_size(self.config.CONTEXT_WINDOW_SIZE)

            self._sync_component_state()
            return self.settings.copy()
        except Exception as e:
            logger.error(f"SETTINGS_SERVICE: Error resetting settings: {e}")
            raise
