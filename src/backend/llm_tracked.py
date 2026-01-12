"""
Tracked LLM Engine with LiteLLM + Opik Integration
===================================================

This module provides LLM inference with automatic Opik tracing for:
- Token counting (input/output/total)
- Latency tracking
- Cost estimation
- Proper nested spans in trace hierarchy

Uses LiteLLM to wrap Groq calls with OpikLogger callback.
"""

import os
from typing import Optional
import litellm
from litellm.integrations.opik.opik import OpikLogger

from .config import settings
from .logger_config import logger

# Configure LiteLLM for Groq
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY or ""

# Initialize Opik logger for LiteLLM
opik_logger = OpikLogger()
litellm.callbacks = [opik_logger]

# Set project name for traces
os.environ["OPIK_PROJECT_NAME"] = os.getenv("OPIK_PROJECT_NAME", "rag-system")


class TrackedGroqEngine:
    """
    Groq LLM Engine with automatic Opik tracing via LiteLLM.
    
    All LLM calls are automatically logged with:
    - Token usage (input, output, total)
    - Latency
    - Cost estimation
    - Model info
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize tracked Groq LLM engine.
        
        Args:
            model_name: Model name (defaults to settings.LLM_MODEL)
        """
        self.model_name = model_name or settings.LLM_MODEL
        # LiteLLM uses "groq/<model_name>" format
        self.litellm_model = f"groq/{self.model_name}"
        self.model_loaded = self._validate_setup()
        
        if self.model_loaded:
            logger.info(f"TrackedGroqEngine initialized: model={self.litellm_model}")
        else:
            logger.error("TrackedGroqEngine: GROQ_API_KEY not configured")
    
    def _validate_setup(self) -> bool:
        """Validate that API key is configured."""
        api_key = settings.GROQ_API_KEY
        if not api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            return False
        return True
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Generate text using Groq via LiteLLM with Opik tracking.
        
        All calls are automatically traced with token counts, latency, and cost.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            metadata: Optional metadata to include in trace
            
        Returns:
            Generated text
        """
        if not self.model_loaded:
            logger.error("TrackedGroqEngine not initialized")
            return "Error: LLM not initialized. Set GROQ_API_KEY in environment."
        
        if not prompt or not prompt.strip():
            logger.warning("Empty prompt provided")
            return "Error: Empty prompt provided."
        
        try:
            logger.debug(f"TrackedGroqEngine: Generating response (max_tokens={max_tokens}, temperature={temperature})")
            
            # Build metadata for Opik span linking
            call_metadata = metadata or {}
            
            # Make the LLM call via LiteLLM - automatically traced by OpikLogger
            response = litellm.completion(
                model=self.litellm_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                metadata=call_metadata
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Log token usage
            usage = response.usage
            logger.debug(
                f"TrackedGroqEngine: Generated {len(response_text)} chars, "
                f"tokens: {usage.prompt_tokens}+{usage.completion_tokens}={usage.total_tokens}"
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"TrackedGroqEngine: Error generating response: {e}", exc_info=True)
            return f"Error: {str(e)}"
    
    def generate_with_context(
        self,
        prompt: str,
        context: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        span_data: Optional[dict] = None
    ) -> str:
        """
        Generate response with context, linked to parent Opik span.
        
        Args:
            prompt: User's question
            context: Retrieved context from documents
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            span_data: Opik span data for linking (from get_current_span_data())
            
        Returns:
            Generated answer
        """
        # Build metadata for Opik span linking
        metadata = {}
        if span_data:
            metadata["opik"] = {"current_span_data": span_data}
        
        # Build the full prompt with context
        full_prompt = f"""Context from documents:
{context}

User Question: {prompt}

Please provide a helpful answer based on the context above."""
        
        return self.generate(
            prompt=full_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            metadata=metadata
        )
    
    def is_ready(self) -> bool:
        """Check if the engine is ready."""
        return self.model_loaded


def get_tracked_llm_engine():
    """
    Get tracked LLM engine instance.
    
    Returns:
        TrackedGroqEngine instance with Opik integration
    """
    return TrackedGroqEngine()
