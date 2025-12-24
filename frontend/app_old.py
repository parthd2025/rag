"""
RAG Chatbot - Simplified Professional Frontend
Clean, linear, single-page experience
"""

import streamlit as st
import logging
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Configuration
from config import API_URL, REQUEST_TIMEOUT, PAGE_TITLE, PAGE_ICON
from utils.api_client import get_api_client
from utils.ui_components import render_custom_css, success_alert, error_alert, info_alert
from components.chat import render_chat_interface, render_quick_actions
from components.documents import render_upload_section, render_document_stats, render_clear_section
from components.quiz import render_quiz_interface, render_quiz_mode
from components.system_info import render_system_dashboard, render_help_section

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

# Initialize session state
if "api_connected" not in st.session_state:
    st.session_state.api_connected = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Apply custom CSS
render_custom_css()


def check_api_connection():
    """Verify API connectivity."""
    try:
        api_client = get_api_client(API_URL, REQUEST_TIMEOUT)
        is_connected = api_client.health_check()
        st.session_state.api_connected = is_connected
        return is_connected, api_client
    except Exception as e:
        logger.error(f"API connection failed: {e}")
        st.session_state.api_connected = False
        return False, None


def main():
    """Main application entry point."""
    
    # Header
    st.markdown("# 🤖 RAG Chatbot - Simple & Fast")
    st.markdown("*Ask questions about your documents*")
    st.divider()
    
    # Check API connection
    is_connected, api_client = check_api_connection()
    
    if not is_connected:
        st.error(f"❌ Cannot connect to API at {API_URL}")
        st.info("""
        **Start the backend first:**
        ```bash
        cd backend && python main.py
        ```
        """)
        return
    
    st.success("✅ Connected to backend")
    
    # Sidebar Navigation (Simple)
    st.sidebar.title("📍 Navigation")
    page = st.sidebar.radio(
        "Go to:",
        ["💬 Chat", "📤 Upload", "🎯 Quiz", "⚙️ Settings"],
        key="page_selector"
    )
    
    st.sidebar.divider()
    
    # Quick Stats
    try:
        docs_info = api_client.get_documents()
        if docs_info:
            st.sidebar.metric("📊 Total Chunks", docs_info.get("total_chunks", 0))
            st.sidebar.metric("📄 Documents", len(docs_info.get("documents", [])))
    except:
        pass
    
    st.divider()
    
    # Route to page
    if "Chat" in page:
        render_page_chat(api_client)
    elif "Upload" in page:
        render_page_upload(api_client)
    elif "Quiz" in page:
        render_page_quiz(api_client)
    else:
        render_page_settings(api_client)


def render_page_chat(api_client):
    """Chat page - simple and direct."""
    st.markdown("## 💬 Ask Your Questions")
    
    try:
        docs_info = api_client.get_documents()
        if not docs_info or docs_info.get("total_chunks", 0) == 0:
            st.warning("📭 No documents uploaded yet. Go to Upload tab to add documents.")
            return
        
        render_chat_interface(api_client, {"TOP_K": 5})
        st.divider()
        render_quick_actions(api_client)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")


def render_page_upload(api_client):
    """Upload page - simple and direct."""
    st.markdown("## 📤 Upload Documents")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### Add New Document")
        render_upload_section(api_client)
    
    with col2:
        st.markdown("### Current Library")
        render_document_stats(api_client)
    
    st.divider()
    st.markdown("### 🧹 Data Management")
    render_clear_section(api_client)


def render_page_quiz(api_client):
    """Quiz page - simple and direct."""
    st.markdown("## 🎯 Test Your Knowledge")
    
    try:
        docs_info = api_client.get_documents()
        if not docs_info or docs_info.get("total_chunks", 0) == 0:
            st.warning("📭 No documents available. Please upload documents first.")
            return
        
        if st.session_state.get("quiz_active"):
            render_quiz_mode(api_client)
        else:
            render_quiz_interface(api_client)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")


def render_page_settings(api_client):
    """Settings page - simple and direct."""
    st.markdown("## ⚙️ System Settings")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 System Status")
        render_system_dashboard(api_client)
    
    with col2:
        st.markdown("### ❓ Help")
        render_help_section()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        st.error(f"Application error: {str(e)}")
