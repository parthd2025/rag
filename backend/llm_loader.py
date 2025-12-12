"""
Groq LLM inference engine with improved error handling and configuration.
"""

from typing import Optional
from pathlib import Path

from config import settings
from logger_config import logger


class GroqLLMEngine:
    """Groq LLM inference using llama-3.3-70b-versatile."""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize Groq LLM engine.
        
        Args:
            model_name: Model name (defaults to settings.LLM_MODEL)
        """
        self.model_name = model_name or settings.LLM_MODEL
        self.client = None
        self.model_loaded = False
        self._load_model()
    
    def _load_model(self) -> None:
        """Initialize Groq client."""
        try:
            from groq import Groq
            
            api_key = settings.GROQ_API_KEY
            if not api_key:
                logger.error("GROQ_API_KEY not found in environment variables")
                logger.info("Get a free API key at: https://console.groq.com/keys")
                self.model_loaded = False
                return
            
            self.client = Groq(api_key=api_key)
            self.model_loaded = True
            logger.info(f"Groq client initialized with model: {self.model_name}")
            
        except ImportError:
            logger.error("groq package not installed. Install with: pip install groq")
            self.model_loaded = False
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}", exc_info=True)
            self.model_loaded = False
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using Groq.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        if not self.model_loaded:
            logger.error("Groq not initialized")
            return "Error: Groq not initialized. Set GROQ_API_KEY in environment."
        
        if not prompt or not prompt.strip():
            logger.warning("Empty prompt provided")
            return "Error: Empty prompt provided."
        
        try:
            logger.debug(f"Generating response (max_tokens={max_tokens}, temperature={temperature})")
            message = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_text = message.choices[0].message.content.strip()
            logger.debug(f"Generated response: {len(response_text)} characters")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return f"Error: {str(e)}"
    
    def is_ready(self) -> bool:
        """
        Check if Groq is ready.
        
        Returns:
            True if ready, False otherwise
        """
        return self.model_loaded and self.client is not None


def get_llm_engine(use_groq: bool = True):
    """
    Get LLM engine instance.
    
    Args:
        use_groq: Whether to use Groq (currently only Groq is supported)
        
    Returns:
        LLM engine instance
    """
    if use_groq:
        return GroqLLMEngine()
    else:
        logger.warning("Only Groq is currently supported")
        return GroqLLMEngine()
