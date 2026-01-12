"""
Pages Package
Contains all page modules for the RAG Chatbot
"""

from views.chat import render_chat_page
from views.library import render_library_page
from views.upload import render_upload_page
from views.settings import render_settings_page

__all__ = [
    "render_chat_page",
    "render_library_page", 
    "render_upload_page",
    "render_settings_page"
]
