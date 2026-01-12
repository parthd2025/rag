"""
Components Package
Reusable UI components for the RAG Chatbot
"""

from components.state import (
    init_session_state,
    get_state,
    set_state,
    clear_chat_state,
    update_document_stats,
    navigate_to,
    get_current_page,
    is_api_connected,
    get_api_client,
    set_api_client
)

from components.sidebar import render_sidebar
from components.navbar import render_navbar, render_page_header, render_breadcrumb

# Legacy component exports for backward compatibility
from components.chat import render_chat_interface
from components.documents import render_upload_section, render_document_stats, render_document_management
from components.settings import render_settings_dashboard, render_quick_settings_panel

__all__ = [
    # State management
    "init_session_state",
    "get_state",
    "set_state",
    "clear_chat_state",
    "update_document_stats",
    "navigate_to",
    "get_current_page",
    "is_api_connected",
    "get_api_client",
    "set_api_client",
    # Navigation components
    "render_sidebar",
    "render_navbar",
    "render_page_header",
    "render_breadcrumb",
    # Legacy components
    "render_chat_interface",
    "render_upload_section",
    "render_document_stats",
    "render_document_management",
    "render_settings_dashboard",
    "render_quick_settings_panel"
]
