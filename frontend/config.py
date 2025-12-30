"""
Frontend Configuration - Professional UI/UX Setup
15+ years of expert UI/UX principles
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8001")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# UI Configuration
SIDEBAR_STATE = "expanded"
LAYOUT = "wide"
PAGE_TITLE = "RAG Chatbot - Intelligent Document Q&A"
PAGE_ICON = "🤖"

# Feature Toggles
FEATURES = {
    "chat": True,
    "quiz": True,
    "document_upload": True,
    "document_management": True,
    "system_info": True,
    "source_visualization": True,
    "export_results": True,
}

# UI/UX Settings
COLORS = {
    "primary": "#0078D4",      # Microsoft Blue (trusted)
    "secondary": "#50E6FF",    # Cyan (modern)
    "success": "#107C10",      # Green
    "warning": "#FFB900",      # Orange
    "error": "#E81123",        # Red
    "neutral": "#F3F2F1",      # Light gray
    "text_primary": "#201F1E", # Dark gray
    "text_secondary": "#605E5C" # Medium gray
}

# UI Constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

CHUNK_SIZE_DEFAULT = 1000
TOP_K_DEFAULT = 5
TOP_K_MAX = 20
TEMPERATURE_DEFAULT = 0.7

# Chat Settings
CHAT_MAX_MESSAGES = 50
MESSAGE_RETENTION_MINUTES = 120
AUTO_SCROLL_ENABLED = True

# Loading States
LOADING_MESSAGES = [
    "🔍 Searching your documents...",
    "💭 Thinking about your question...",
    "⚡ Generating answer...",
    "✨ Polishing response...",
]

QUIZ_LOADING_MESSAGES = [
    "📚 Creating questions...",
    "🧠 Generating answers...",
    "✅ Finalizing quiz...",
]

# Timeouts (in seconds)
HEALTH_CHECK_TIMEOUT = 5
UPLOAD_TIMEOUT = 120
CHAT_TIMEOUT = 180
QUIZ_TIMEOUT = 120

# File Upload Settings
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv", ".xlsx", ".pptx", ".html"}

# Streamlit Session Keys
SESSION_KEYS = {
    "api_connected": "api_connected",
    "documents_count": "documents_count",
    "chat_messages": "chat_messages",
    "upload_success": "upload_success",
    "last_query": "last_query",
    "system_status": "system_status",
}

# Professional UI Strings
UI_STRINGS = {
    "welcome": "Welcome to RAG Chatbot",
    "subtitle": "Intelligent Question-Answering from Your Documents",
    "upload_hint": "Drag and drop your documents or click to browse",
    "no_docs": "No documents uploaded yet. Start by uploading a file.",
    "ask_question": "Ask a question about your documents...",
    "generating": "Generating response...",
    "error_occurred": "An error occurred. Please try again.",
    "success": "Success!",
    "copy_to_clipboard": "📋 Copy",
    "share_answer": "📤 Share",
    "feedback": "Was this helpful?",
}

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "logs/frontend_logs/app.log"

# Performance
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour
COMPRESS_RESPONSES = True

# Export Settings
EXPORT_FORMATS = ["PDF", "JSON", "TXT", "CSV"]
