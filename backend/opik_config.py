"""
OPIK Configuration and Initialization Module
=============================================

This module handles all OPIK (Observability) configuration, initialization,
and validation for the RAG system. It ensures:

1. Proper configuration for local/cloud OPIK instances
2. Automatic project creation if it doesn't exist
3. Connection validation before tracing
4. Clear error messages for troubleshooting
5. Singleton pattern for consistent client usage

Environment Variables:
- OPIK_URL_OVERRIDE: URL of OPIK instance (default: http://localhost:5173/api)
- OPIK_WORKSPACE: Workspace name (default: default)
- OPIK_PROJECT_NAME: Project name (default: rag-system)
- OPIK_API_KEY: API key (use "local" for local instances)
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)

# Configuration defaults - Opik Cloud
DEFAULT_OPIK_URL = "https://www.comet.com/opik/api"
DEFAULT_OPIK_WORKSPACE = "parth-d"
DEFAULT_PROJECT_NAME = "rag-system"


class OpikConfig:
    """Configuration class for OPIK integration."""
    
    def __init__(self):
        self.url_override = os.getenv("OPIK_URL_OVERRIDE", DEFAULT_OPIK_URL)
        self.workspace = os.getenv("OPIK_WORKSPACE", DEFAULT_OPIK_WORKSPACE)
        self.project_name = os.getenv("OPIK_PROJECT_NAME", DEFAULT_PROJECT_NAME)
        self.api_key = os.getenv("OPIK_API_KEY", "local")
        self.enabled = os.getenv("OPIK_ENABLED", "true").lower() == "true"
        
        # Ensure URL ends with /api if it's a local instance
        if self.url_override and "/api" not in self.url_override:
            self.url_override = self.url_override.rstrip("/") + "/api"
    
    def __repr__(self) -> str:
        return (
            f"OpikConfig(url={self.url_override}, workspace={self.workspace}, "
            f"project={self.project_name}, enabled={self.enabled})"
        )


class OpikManager:
    """
    Singleton manager for OPIK client and tracing.
    
    Handles:
    - Client initialization with proper configuration
    - Connection validation
    - Project existence verification and creation
    - Error handling and logging
    """
    
    _instance: Optional["OpikManager"] = None
    _initialized: bool = False
    
    def __new__(cls) -> "OpikManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if OpikManager._initialized:
            return
        
        self.config = OpikConfig()
        self.client = None
        self.available = False
        self.initialization_error: Optional[str] = None
        
        OpikManager._initialized = True
        
        # Auto-initialize if enabled
        if self.config.enabled:
            self._initialize()
    
    def _initialize(self) -> bool:
        """
        Initialize OPIK client with proper configuration.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            import opik
            from opik import Opik
            
            logger.info(f"OPIK_INIT: Starting OPIK initialization...")
            logger.info(f"OPIK_INIT: Config: {self.config}")
            
            # Step 1: Configure OPIK for cloud usage
            is_local = "localhost" in self.config.url_override or "127.0.0.1" in self.config.url_override
            
            logger.info(f"OPIK_INIT: Configuring OPIK (local={is_local}, workspace={self.config.workspace})")
            
            try:
                # Configure OPIK SDK for cloud or local
                if is_local:
                    opik.configure(
                        use_local=True,
                        url=self.config.url_override.replace("/api", ""),
                        force=True,
                        automatic_approvals=True
                    )
                else:
                    # Cloud configuration - use API key
                    opik.configure(
                        api_key=self.config.api_key,
                        workspace=self.config.workspace,
                        force=True,
                        automatic_approvals=True
                    )
                logger.info(f"OPIK_INIT: OPIK configured successfully for {'local' if is_local else 'cloud'} mode")
            except Exception as config_error:
                logger.warning(f"OPIK_INIT: Configuration warning (may be already configured): {config_error}")
            
            # Step 2: Create OPIK client
            logger.info(f"OPIK_INIT: Creating OPIK client for project '{self.config.project_name}'")
            
            if is_local:
                self.client = Opik(
                    project_name=self.config.project_name,
                    workspace=self.config.workspace,
                    host=self.config.url_override
                )
            else:
                # Cloud client - uses configured API key and workspace
                self.client = Opik(
                    project_name=self.config.project_name,
                    workspace=self.config.workspace
                )
            
            logger.info(f"OPIK_INIT: OPIK client created successfully")
            logger.info(f"OPIK_INIT: Project name: {self.client.project_name}")
            
            # Step 3: Validate connection by checking auth
            logger.info(f"OPIK_INIT: Validating connection...")
            
            try:
                self.client.auth_check()
                logger.info(f"OPIK_INIT: Connection validated - auth check passed")
            except Exception as auth_error:
                # For local instances without auth, this might fail but tracing still works
                logger.warning(f"OPIK_INIT: Auth check skipped (common for local instances): {auth_error}")
            
            # Step 4: Test trace creation to ensure project is created
            logger.info(f"OPIK_INIT: Creating test trace to ensure project exists...")
            
            test_trace = self.client.trace(
                name="opik_initialization_test",
                input={"test": "initialization", "purpose": "verify_project_creation"},
                tags=["system", "initialization"],
                metadata={"auto_generated": True}
            )
            test_trace.end(output={"status": "success", "message": "OPIK initialized successfully"})
            
            # Flush to ensure the trace is sent and project is created
            self.client.flush()
            
            logger.info(f"OPIK_INIT: Test trace created and flushed successfully")
            logger.info(f"OPIK_INIT: Project '{self.config.project_name}' should now appear in OPIK UI")
            
            self.available = True
            self.initialization_error = None
            
            logger.info(f"OPIK_INIT: ✅ OPIK initialization complete!")
            logger.info(f"OPIK_INIT: ✅ View traces at: {self.config.url_override.replace('/api', '')}")
            
            return True
            
        except ImportError as e:
            self.available = False
            self.initialization_error = f"OPIK package not installed: {e}"
            logger.error(f"OPIK_INIT: ❌ {self.initialization_error}")
            logger.error("OPIK_INIT: Install with: pip install opik")
            return False
            
        except Exception as e:
            self.available = False
            self.initialization_error = f"OPIK initialization failed: {e}"
            logger.error(f"OPIK_INIT: ❌ {self.initialization_error}", exc_info=True)
            return False
    
    def reinitialize(self) -> bool:
        """
        Force re-initialization of OPIK client.
        
        Useful after:
        - Configuration changes
        - Connection issues
        - Project deletion in OPIK UI
        
        Returns:
            bool: True if re-initialization successful
        """
        logger.info("OPIK_INIT: Re-initializing OPIK client...")
        self.client = None
        self.available = False
        self.initialization_error = None
        self.config = OpikConfig()  # Reload config from environment
        return self._initialize()
    
    def get_client(self) -> Optional[Any]:
        """
        Get the OPIK client instance.
        
        Returns:
            Opik client if available, None otherwise
        """
        if not self.available and self.config.enabled:
            logger.warning("OPIK_INIT: Client not available, attempting re-initialization...")
            self._initialize()
        
        return self.client if self.available else None
    
    def create_trace(
        self,
        name: str,
        input: Optional[Dict[str, Any]] = None,
        tags: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Create a new trace with error handling.
        
        Args:
            name: Name of the trace
            input: Input data for the trace
            tags: Tags for categorization
            metadata: Additional metadata
            
        Returns:
            Trace object if successful, None otherwise
        """
        client = self.get_client()
        if not client:
            logger.warning(f"OPIK_TRACE: Cannot create trace '{name}' - client not available")
            return None
        
        try:
            trace = client.trace(
                name=name,
                input=input or {},
                tags=tags or [],
                metadata=metadata or {}
            )
            logger.debug(f"OPIK_TRACE: Created trace '{name}' with ID: {getattr(trace, 'id', 'unknown')}")
            return trace
        except Exception as e:
            logger.error(f"OPIK_TRACE: Failed to create trace '{name}': {e}")
            return None
    
    def flush(self) -> bool:
        """
        Flush all pending traces to OPIK.
        
        Returns:
            bool: True if flush successful
        """
        if not self.client:
            return False
        
        try:
            self.client.flush()
            logger.debug("OPIK_TRACE: Flushed traces successfully")
            return True
        except Exception as e:
            logger.error(f"OPIK_TRACE: Flush failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current OPIK status for debugging.
        
        Returns:
            Dict with status information
        """
        return {
            "available": self.available,
            "enabled": self.config.enabled,
            "url": self.config.url_override,
            "workspace": self.config.workspace,
            "project_name": self.config.project_name,
            "initialization_error": self.initialization_error,
            "client_initialized": self.client is not None
        }


# Singleton instance
_opik_manager: Optional[OpikManager] = None


def get_opik_manager() -> OpikManager:
    """
    Get the singleton OPIK manager instance.
    
    Returns:
        OpikManager instance
    """
    global _opik_manager
    if _opik_manager is None:
        _opik_manager = OpikManager()
    return _opik_manager


def initialize_opik() -> Tuple[bool, str]:
    """
    Initialize OPIK and return status.
    
    This is the main entry point for OPIK initialization.
    Call this at application startup.
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    manager = get_opik_manager()
    
    if not manager.config.enabled:
        return False, "OPIK is disabled via configuration"
    
    if manager.available:
        return True, f"OPIK already initialized for project '{manager.config.project_name}'"
    
    success = manager.reinitialize()
    
    if success:
        return True, f"OPIK initialized successfully for project '{manager.config.project_name}'"
    else:
        return False, f"OPIK initialization failed: {manager.initialization_error}"


def get_opik_client() -> Optional[Any]:
    """
    Get the OPIK client for creating traces.
    
    Returns:
        Opik client if available, None otherwise
    """
    return get_opik_manager().get_client()


def create_rag_trace(
    query: str,
    top_k: int = 5,
    temperature: float = 0.7,
    user_id: Optional[str] = None
) -> Optional[Any]:
    """
    Create a trace specifically for RAG queries.
    
    Args:
        query: User's question
        top_k: Number of chunks to retrieve
        temperature: LLM temperature
        user_id: Optional user identifier
        
    Returns:
        Trace object if successful, None otherwise
    """
    return get_opik_manager().create_trace(
        name="rag_query",
        input={
            "query": query,
            "query_length": len(query),
            "top_k": top_k,
            "temperature": temperature,
            "user_id": user_id or "anonymous"
        },
        tags=["rag", "production", "query"],
        metadata={
            "system": "rag-chatbot",
            "version": "1.0"
        }
    )


# Create no-op decorator for when OPIK is not available
def _noop_track(*args, **kwargs):
    """No-op decorator when OPIK is not available."""
    def decorator(func):
        return func
    return decorator


def get_track_decorator():
    """
    Get the track decorator with fallback.
    
    Returns:
        opik.track decorator if available, no-op decorator otherwise
    """
    try:
        from opik import track
        return track
    except ImportError:
        return _noop_track


# Convenience export
track = get_track_decorator()
