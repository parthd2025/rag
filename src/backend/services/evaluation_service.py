"""
LLM-Based Answer Evaluation Service with OPIK Integration
==========================================================

Provides automatic scoring for RAG responses using LLM-as-judge:
- Relevance: How relevant is the answer to the question?
- Faithfulness: Is the answer grounded in the retrieved context?
- Completeness: Does the answer fully address the question?

Scores are tracked in OPIK for comparison and analysis.
"""

import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from ..logger_config import logger
from ..config import settings
from ..opik_config import get_opik_manager

# Try to import opik tracking
try:
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    def track(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


@dataclass
class EvaluationScores:
    """Evaluation scores for a RAG response."""
    relevance: float  # 0-1: How relevant is the answer to the question
    faithfulness: float  # 0-1: Is the answer grounded in the context
    completeness: float  # 0-1: Does the answer fully address the question
    overall: float  # Weighted average
    model_used: str  # Which model generated the response
    evaluation_model: str  # Which model did the evaluation
    reasoning: Dict[str, str]  # Reasoning for each score
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LLMEvaluator:
    """
    LLM-based evaluator for RAG responses.
    
    Uses an LLM to score responses on:
    - Relevance
    - Faithfulness  
    - Completeness
    """
    
    EVALUATION_PROMPT = """You are an expert evaluator for a RAG (Retrieval-Augmented Generation) system.
Your task is to evaluate the quality of an AI-generated answer based on the question and retrieved context.

QUESTION: {question}

RETRIEVED CONTEXT:
{context}

GENERATED ANSWER:
{answer}

Evaluate the answer on these three criteria (score 0.0 to 1.0):

1. RELEVANCE (0.0-1.0): How relevant is the answer to the question?
   - 1.0: Directly answers the question with appropriate detail
   - 0.5: Partially relevant, addresses some aspects
   - 0.0: Completely irrelevant or off-topic

2. FAITHFULNESS (0.0-1.0): Is the answer grounded in the retrieved context?
   - 1.0: All claims are supported by the context
   - 0.5: Some claims are supported, some are not
   - 0.0: Answer contains hallucinations or unsupported claims

3. COMPLETENESS (0.0-1.0): Does the answer fully address the question?
   - 1.0: Comprehensive answer covering all aspects
   - 0.5: Addresses main points but misses some details
   - 0.0: Very incomplete or superficial

Respond in this exact JSON format:
{{
    "relevance": <score>,
    "faithfulness": <score>,
    "completeness": <score>,
    "relevance_reasoning": "<brief explanation>",
    "faithfulness_reasoning": "<brief explanation>",
    "completeness_reasoning": "<brief explanation>"
}}

IMPORTANT: Only respond with valid JSON, no other text."""

    def __init__(self, evaluation_model: str = "llama-3.3-70b-versatile"):
        """
        Initialize evaluator with specified model.
        
        Args:
            evaluation_model: Model to use for evaluation
        """
        self.evaluation_model = evaluation_model
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Groq client for evaluation."""
        try:
            from groq import Groq
            api_key = settings.GROQ_API_KEY
            if api_key:
                self.client = Groq(api_key=api_key)
                logger.info(f"LLMEvaluator initialized with model: {self.evaluation_model}")
            else:
                logger.warning("No GROQ_API_KEY found for evaluation")
        except ImportError:
            logger.error("groq package not installed")
        except Exception as e:
            logger.error(f"Error initializing evaluator: {e}")
    
    @track(
        name="llm_evaluation",
        project_name="rag-system",
        tags=["evaluation", "scoring"]
    )
    def evaluate(
        self,
        question: str,
        context: str,
        answer: str,
        model_used: str
    ) -> EvaluationScores:
        """
        Evaluate a RAG response using LLM-as-judge.
        
        Args:
            question: The user's question
            context: The retrieved context used for generation
            answer: The generated answer
            model_used: Which model generated the answer
            
        Returns:
            EvaluationScores with relevance, faithfulness, completeness
        """
        if not self.client:
            logger.warning("Evaluator client not available, returning default scores")
            return self._default_scores(model_used)
        
        try:
            prompt = self.EVALUATION_PROMPT.format(
                question=question,
                context=context[:4000],  # Truncate context if too long
                answer=answer
            )
            
            response = self.client.chat.completions.create(
                model=self.evaluation_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent scoring
            )
            
            result_text = response.choices[0].message.content.strip()
            scores = self._parse_scores(result_text, model_used)
            
            logger.info(
                f"Evaluation complete - Relevance: {scores.relevance:.2f}, "
                f"Faithfulness: {scores.faithfulness:.2f}, "
                f"Completeness: {scores.completeness:.2f}"
            )
            
            return scores
            
        except Exception as e:
            logger.error(f"Evaluation error: {e}", exc_info=True)
            return self._default_scores(model_used)
    
    def _parse_scores(self, result_text: str, model_used: str) -> EvaluationScores:
        """Parse LLM evaluation response into scores."""
        import json
        
        try:
            # Try to extract JSON from response
            result_text = result_text.strip()
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            data = json.loads(result_text)
            
            relevance = float(data.get("relevance", 0.5))
            faithfulness = float(data.get("faithfulness", 0.5))
            completeness = float(data.get("completeness", 0.5))
            
            # Clamp values to 0-1
            relevance = max(0.0, min(1.0, relevance))
            faithfulness = max(0.0, min(1.0, faithfulness))
            completeness = max(0.0, min(1.0, completeness))
            
            # Calculate weighted overall score
            overall = (relevance * 0.35) + (faithfulness * 0.40) + (completeness * 0.25)
            
            return EvaluationScores(
                relevance=relevance,
                faithfulness=faithfulness,
                completeness=completeness,
                overall=overall,
                model_used=model_used,
                evaluation_model=self.evaluation_model,
                reasoning={
                    "relevance": data.get("relevance_reasoning", ""),
                    "faithfulness": data.get("faithfulness_reasoning", ""),
                    "completeness": data.get("completeness_reasoning", "")
                }
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse evaluation response: {e}")
            return self._default_scores(model_used)
    
    def _default_scores(self, model_used: str) -> EvaluationScores:
        """Return default scores when evaluation fails."""
        return EvaluationScores(
            relevance=0.5,
            faithfulness=0.5,
            completeness=0.5,
            overall=0.5,
            model_used=model_used,
            evaluation_model=self.evaluation_model,
            reasoning={
                "relevance": "Evaluation not available",
                "faithfulness": "Evaluation not available",
                "completeness": "Evaluation not available"
            }
        )


class ModelComparisonService:
    """
    Service for comparing responses from multiple LLM models.
    
    Runs the same query through different models and evaluates each response.
    """
    
    # Available models for comparison (all Groq models)
    AVAILABLE_MODELS = [
        "llama-3.3-70b-versatile",                      # Groq - Llama 3.3 70B
        "meta-llama/llama-4-maverick-17b-128e-instruct", # Groq - Llama 4 Maverick
        "openai/gpt-oss-20b",                           # Groq - GPT-OSS 20B
        "qwen/qwen3-32b",                               # Groq - Qwen3 32B
    ]
    
    # Model provider mapping - all are Groq models
    MODEL_PROVIDERS = {
        "llama-3.3-70b-versatile": "groq",
        "meta-llama/llama-4-maverick-17b-128e-instruct": "groq",
        "openai/gpt-oss-20b": "groq",
        "qwen/qwen3-32b": "groq",
    }
    
    def __init__(self, rag_engine):
        """
        Initialize comparison service.
        
        Args:
            rag_engine: The RAG engine instance for context retrieval
        """
        self.rag_engine = rag_engine
        self.evaluator = LLMEvaluator(evaluation_model="llama-3.3-70b-versatile")
        self.opik_manager = get_opik_manager()
        
        # Initialize clients for multiple providers
        self.groq_client = None
        self.openai_client = None
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize Groq and OpenAI clients."""
        # Initialize Groq
        try:
            from groq import Groq
            groq_key = settings.GROQ_API_KEY
            if groq_key:
                self.groq_client = Groq(api_key=groq_key)
                logger.info("Groq client initialized")
        except Exception as e:
            logger.warning(f"Groq initialization failed: {e}")
        
        # Initialize OpenAI
        try:
            from openai import OpenAI
            openai_key = settings.OPENAI_API_KEY
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized")
            else:
                logger.warning("No OPENAI_API_KEY found")
        except ImportError:
            logger.warning("openai package not installed. Install with: pip install openai")
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}", exc_info=True)
    
    @track(
        name="model_comparison",
        project_name="rag-system",
        tags=["comparison", "evaluation", "multi-model"]
    )
    async def compare_models(
        self,
        query: str,
        models: Optional[List[str]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Compare responses from multiple models for the same query.
        
        Args:
            query: The user's question
            models: List of model names to compare (defaults to top 2)
            top_k: Number of documents to retrieve
            
        Returns:
            Comparison results with scores for each model
        """
        # Default to ALL available models
        if models is None:
            models = self.AVAILABLE_MODELS.copy()
        
        # Validate models
        models = [m for m in models if m in self.AVAILABLE_MODELS]
        if not models:
            models = self.AVAILABLE_MODELS.copy()
        
        start_time = time.time()
        
        # Step 1: Retrieve context (shared across all models)
        context_result = await self._retrieve_context(query, top_k)
        context = context_result.get("context", "")
        sources = context_result.get("sources", [])
        
        if not context:
            return {
                "error": "No relevant context found",
                "query": query,
                "results": []
            }
        
        # Step 2: Generate answers from each model
        results = []
        for model in models:
            model_result = await self._generate_and_evaluate(
                query=query,
                context=context,
                model=model
            )
            results.append(model_result)
        
        # Step 3: Rank models by overall score
        results.sort(key=lambda x: x.get("scores", {}).get("overall", 0), reverse=True)
        
        comparison_time = time.time() - start_time
        
        return {
            "query": query,
            "models_compared": len(results),
            "comparison_time": round(comparison_time, 2),
            "context_chunks": len(sources),
            "results": results,
            "best_model": results[0]["model"] if results else None,
            "sources": sources[:3]  # Include top 3 sources
        }
    
    async def _retrieve_context(self, query: str, top_k: int) -> Dict[str, Any]:
        """Retrieve context using the RAG engine."""
        try:
            # Use the RAG engine's retrieve_context method
            result = self.rag_engine.retrieve_context(query, top_k=top_k)
            
            if not result or not result.get("chunks"):
                return {"context": "", "sources": []}
            
            # Build context from chunks
            context_parts = []
            sources = []
            
            chunks = result.get("chunks", [])
            metadata = result.get("metadata", [])
            
            for i, chunk in enumerate(chunks):
                context_parts.append(f"[Source {i+1}]: {chunk}")
                
                meta = metadata[i] if i < len(metadata) else {}
                sources.append({
                    "document": meta.get("source_doc", "Unknown"),
                    "relevance": meta.get("relevance_score", 0),
                    "preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
                })
            
            return {
                "context": "\n\n".join(context_parts),
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return {"context": "", "sources": []}
    
    def _get_client(self, model: str):
        """Get the appropriate client for a model."""
        provider = self.MODEL_PROVIDERS.get(model, "groq")
        if provider == "openai":
            return self.openai_client
        return self.groq_client
    
    @track(
        name="generate_and_evaluate",
        project_name="rag-system",
        tags=["generation", "evaluation"]
    )
    async def _generate_and_evaluate(
        self,
        query: str,
        context: str,
        model: str
    ) -> Dict[str, Any]:
        """Generate answer with a specific model and evaluate it."""
        start_time = time.time()
        
        try:
            # Get the right client for this model
            client = self._get_client(model)
            if not client:
                raise Exception(f"No client available for model {model}")
            
            # Build prompt
            prompt = self._build_prompt(query, context)
            
            # Generate answer
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
            
            answer = response.choices[0].message.content.strip()
            generation_time = time.time() - start_time
            
            # Evaluate the answer
            scores = self.evaluator.evaluate(
                question=query,
                context=context,
                answer=answer,
                model_used=model
            )
            
            return {
                "model": model,
                "answer": answer,
                "generation_time": round(generation_time, 3),
                "scores": scores.to_dict(),
                "tokens": {
                    "prompt": response.usage.prompt_tokens if response.usage else 0,
                    "completion": response.usage.completion_tokens if response.usage else 0,
                    "total": response.usage.total_tokens if response.usage else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Generation error for {model}: {e}")
            return {
                "model": model,
                "answer": f"Error: {str(e)}",
                "generation_time": time.time() - start_time,
                "scores": self.evaluator._default_scores(model).to_dict(),
                "error": str(e)
            }
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build the RAG prompt."""
        return f"""You are a helpful assistant that answers questions based on the provided context.
Use only the information from the context to answer. If the context doesn't contain relevant information, say so.

CONTEXT:
{context}

QUESTION: {query}

Provide a clear, accurate, and complete answer based on the context above."""

    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available models for comparison."""
        return [
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "description": "Groq - Fast & powerful (70B params)"},
            {"id": "meta-llama/llama-4-maverick-17b-128e-instruct", "name": "Llama 4 Maverick 17B", "description": "Groq - Latest Llama 4 (17B params)"},
            {"id": "openai/gpt-oss-20b", "name": "GPT-OSS 20B", "description": "Groq - Open-source GPT (20B params)"},
            {"id": "qwen/qwen3-32b", "name": "Qwen3 32B", "description": "Groq - Alibaba Qwen3 (32B params)"},
        ]


# Convenience function to get service instance
def get_evaluation_service(rag_engine) -> ModelComparisonService:
    """Get a ModelComparisonService instance."""
    return ModelComparisonService(rag_engine)
