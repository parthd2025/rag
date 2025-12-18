"""API client utilities."""

import requests
import json
from typing import Dict, List, Any, Optional
import streamlit as st


class APIClient:
    """HTTP client for backend API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 30
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=self.timeout)
            elif method == "POST":
                response = requests.post(url, json=json_data, files=files, timeout=self.timeout)
            elif method == "PUT":
                response = requests.put(url, json=json_data, timeout=self.timeout)
            elif method == "DELETE":
                response = requests.delete(url, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
            raise
    
    def chat(self, query: str, top_k: int = 5, temperature: float = 0.7) -> Dict:
        """Send chat query to API."""
        return self._make_request(
            "POST",
            "/chat",
            json_data={"query": query, "top_k": top_k, "temperature": temperature}
        )
    
    def get_documents(self) -> Dict:
        """Get list of uploaded documents."""
        return self._make_request("GET", "/documents")
    
    def upload_documents(self, files: List) -> Dict:
        """Upload documents."""
        files_dict = {f"files": (f.name, f, f.type) for f in files}
        return self._make_request("POST", "/documents/upload", files=files_dict)
    
    def clear_documents(self) -> Dict:
        """Clear all documents."""
        return self._make_request("DELETE", "/documents/clear")
    
    def get_health(self) -> Dict:
        """Check API health."""
        return self._make_request("GET", "/health")
    
    def generate_quiz(self, num_questions: int = 5) -> Dict:
        """Generate suggested questions."""
        return self._make_request(
            "POST",
            "/quiz",
            params={"num_questions": num_questions}
        )
    
    def get_settings(self) -> Dict:
        """Get current settings."""
        return self._make_request("GET", "/settings")
    
    def update_settings(self, settings: Dict) -> Dict:
        """Update settings."""
        return self._make_request("PUT", "/settings", json_data=settings)
    
    def reset_settings(self) -> Dict:
        """Reset settings to defaults."""
        return self._make_request("POST", "/settings/reset")


@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance."""
    return APIClient()
