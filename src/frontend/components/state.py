"""
Shared Session State Management
Centralized state for the RAG Chatbot application
"""

import streamlit as st
from typing import Any, Optional
import time


def init_session_state():
    """Initialize all session state variables."""
    
    # Navigation state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "chat"
    
    # API connection state
    if "api_connected" not in st.session_state:
        st.session_state.api_connected = False
    
    if "api_client" not in st.session_state:
        st.session_state.api_client = None
    
    # Chat state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = str(int(time.time()))
    
    # Document state
    if "documents" not in st.session_state:
        st.session_state.documents = []
    
    if "total_chunks" not in st.session_state:
        st.session_state.total_chunks = 0
    
    if "total_docs" not in st.session_state:
        st.session_state.total_docs = 0
    
    # Settings state
    if "max_file_size_mb" not in st.session_state:
        st.session_state.max_file_size_mb = 100
    
    # UI state
    if "sidebar_expanded" not in st.session_state:
        st.session_state.sidebar_expanded = True


def get_state(key: str, default: Any = None) -> Any:
    """Get a value from session state with optional default."""
    return st.session_state.get(key, default)


def set_state(key: str, value: Any):
    """Set a value in session state."""
    st.session_state[key] = value


def clear_chat_state():
    """Clear all chat-related state."""
    st.session_state.chat_messages = []
    st.session_state.conversation_history = []
    st.session_state.chat_id = str(int(time.time()))


def update_document_stats(docs_data: dict):
    """Update document statistics in session state."""
    if docs_data:
        st.session_state.documents = docs_data.get("documents", [])
        st.session_state.total_chunks = docs_data.get("chunks", 0)
        st.session_state.total_docs = len(docs_data.get("documents", []))


def navigate_to(page: str):
    """Navigate to a specific page."""
    valid_pages = ["chat", "library", "upload", "settings"]
    if page in valid_pages:
        st.session_state.current_page = page


def get_current_page() -> str:
    """Get the current active page."""
    return st.session_state.get("current_page", "chat")


def is_api_connected() -> bool:
    """Check if API is connected."""
    return st.session_state.get("api_connected", False)


def get_api_client():
    """Get the API client from session state."""
    return st.session_state.get("api_client", None)


def set_api_client(client, connected: bool = True):
    """Set the API client in session state."""
    st.session_state.api_client = client
    st.session_state.api_connected = connected
