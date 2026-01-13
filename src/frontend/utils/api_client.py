"""
API Client - Professional REST API Integration
Handles all backend communication with retry logic and error handling
"""

import requests
import streamlit as st
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Professional API client with advanced error handling and retry logic."""
    
    def __init__(self, base_url: str, timeout: int = 30, max_retries: int = 3):
        """Initialize API client with configuration."""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """Setup session with headers and optimizations."""
        self.session.headers.update({
            "User-Agent": "RAG-Chatbot-Frontend/1.0",
            "Accept": "application/json",
        })
    
    def health_check(self) -> bool:
        """Check if backend is healthy and responsive."""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5,
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Retrieve system configuration from backend."""
        try:
            response = self.session.get(
                f"{self.base_url}/config",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get config: {e}")
            return None
    
    def upload_document(self, file_data: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """Upload single document to backend with retry logic."""
        # Backend expects a list of files, so we need to send as 'files' not 'file'
        files = [("files", (filename, file_data))]
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/upload",
                    files=files,
                    timeout=120,
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Upload timeout, retrying... ({attempt + 1}/{self.max_retries})")
            except Exception as e:
                logger.error(f"Upload failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
        
        return None

    def upload_multiple_documents(self, files_data: List[tuple]) -> Optional[Dict[str, Any]]:
        """Upload multiple documents at once to backend."""
        # files_data is list of (file_data, filename) tuples
        files = [("files", (filename, file_data)) for file_data, filename in files_data]
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/upload",
                    files=files,
                    timeout=300,  # Longer timeout for multiple files
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Bulk upload timeout, retrying... ({attempt + 1}/{self.max_retries})")
            except Exception as e:
                logger.error(f"Bulk upload failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
        
        return None
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        stream: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Submit question and get answer with sources, optionally with streaming."""
        payload = {
            "question": question,
            "top_k": top_k
        }
        
        try:
            if stream:
                return self._query_stream(payload)
            else:
                return self._query_standard(payload)
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request timed out after {self.timeout}s")
        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response.status_code == 404:
                raise ValueError("No documents uploaded. Please upload documents first.")
            raise
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def _query_standard(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Standard non-streaming query."""
        response = self.session.post(
            f"{self.base_url}/chat",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
    
    def _query_stream(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Streaming query implementation (fallback to standard for now)."""
        # Note: Streaming requires backend implementation
        # For now, fall back to standard query
        logger.info("Streaming requested but not yet implemented, using standard query")
        return self._query_standard(payload)
    
    def compare_models(
        self,
        question: str,
        models: Optional[List[str]] = None,
        top_k: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Compare responses from multiple models with automatic evaluation."""
        payload = {
            "question": question,
            "top_k": top_k
        }
        
        if models:
            payload["models"] = models
        
        try:
            response = self.session.post(
                f"{self.base_url}/compare-models",
                json=payload,
                timeout=self.timeout * 2,  # Comparison takes longer
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Model comparison failed: {e}")
            raise
    
    def get_available_models(self) -> Optional[Dict[str, Any]]:
        """Get list of available models for comparison."""
        try:
            response = self.session.get(
                f"{self.base_url}/available-models",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return None
    
    def generate_suggested_questions(self, num_questions: int = 5) -> Optional[Dict[str, Any]]:
        """Generate suggested questions from uploaded documents."""
        payload = {"num_questions": min(num_questions, 20)}
        
        try:
            response = self.session.post(
                f"{self.base_url}/suggested-questions",
                json=payload,
                timeout=30,  # Reduced timeout for faster response
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Suggested questions generation failed: {e}")
            raise
    
    def get_documents(self) -> Optional[Dict[str, Any]]:
        """Get document statistics."""
        try:
            response = self.session.get(
                f"{self.base_url}/documents",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            return None
    
    def clear_data(self) -> bool:
        """Clear all data from backend."""
        try:
            response = self.session.delete(
                f"{self.base_url}/clear",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Clear data failed: {e}")
            return False
    
    def delete_document(self, document_name: str) -> bool:
        """Delete a specific document from the backend."""
        try:
            response = self.session.delete(
                f"{self.base_url}/documents/{document_name}",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Delete document failed: {e}")
            return False
    
    def get_document_status(self, document_name: str) -> Optional[Dict[str, Any]]:
        """Get status information for a specific document."""
        try:
            response = self.session.get(
                f"{self.base_url}/documents/{document_name}/status",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get document status failed: {e}")
            return None
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update system settings."""
        try:
            response = self.session.put(
                f"{self.base_url}/settings",
                json=settings,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Update settings failed: {e}")
            return False


class APIError(Exception):
    """Custom exception for API errors."""
    pass


class ConnectionError(APIError):
    """Raised when connection to backend fails."""
    pass


class ValidationError(APIError):
    """Raised when input validation fails."""
    pass


@st.cache_resource
def get_api_client(base_url: str, timeout: int = 30) -> APIClient:
    """Get cached API client instance."""
    return APIClient(base_url, timeout=timeout)
