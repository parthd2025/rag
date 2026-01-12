"""
RAG Chatbot - Modular Multi-Page Frontend
A clean, organized Streamlit application with sidebar navigation
"""

import streamlit as st
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import API_URL, REQUEST_TIMEOUT, PAGE_TITLE, PAGE_ICON
from utils.api_client import get_api_client
from components.state import (
    init_session_state, 
    set_api_client, 
    update_document_stats,
    get_current_page,
    is_api_connected
)
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from views.chat import render_chat_page
from views.library import render_library_page
from views.upload import render_upload_page
from views.settings import render_settings_page

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_custom_css():
    """Load custom CSS for modern styling."""
    st.markdown("""
    <style>
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        }
        
        [data-testid="stSidebar"] .stButton button {
            border-radius: 8px;
            margin: 2px 0;
            transition: all 0.2s ease;
        }
        
        [data-testid="stSidebar"] .stButton button:hover {
            transform: translateX(4px);
        }
        
        /* Card-like containers */
        .stExpander {
            border-radius: 10px;
            border: 1px solid #333;
        }
        
        /* Metric cards */
        [data-testid="metric-container"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Button styling */
        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #0068c9 0%, #0052a3 100%);
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }
        
        .stButton button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 104, 201, 0.4);
        }
        
        /* Text input styling */
        .stTextArea textarea {
            border-radius: 10px;
            border: 1px solid #404040;
        }
        
        /* Divider styling */
        hr {
            border-color: #333;
            margin: 1.5rem 0;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Success/Error message styling */
        .stSuccess, .stError, .stWarning, .stInfo {
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)


def check_api_connection():
    """Check API connection and update state."""
    try:
        api = get_api_client(API_URL, REQUEST_TIMEOUT)
        connected = api.health_check()
        set_api_client(api, connected)
        
        if connected:
            # Update document stats
            docs = api.get_documents()
            if docs:
                update_document_stats(docs)
        
        return connected, api
    except Exception as e:
        logger.error(f"API connection error: {e}")
        set_api_client(None, False)
        return False, None


def render_disconnected_state():
    """Render the disconnected state UI."""
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem;">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🔌</h1>
        <h2>Cannot Connect to Backend</h2>
        <p style="color: #888; margin: 1rem 0;">
            The RAG Chatbot backend is not responding.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.error(f"❌ Cannot connect to API at `{API_URL}`")
    
    st.markdown("### 🛠️ How to Fix")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Start the Backend:**
        ```bash
        cd src/backend
        python main.py
        ```
        """)
    
    with col2:
        st.markdown("""
        **Or using the script:**
        ```bash
        python -m src.backend.main
        ```
        """)
    
    st.info("💡 The backend needs to be running on `http://localhost:8000` by default.")
    
    if st.button("🔄 Retry Connection", type="primary"):
        st.rerun()


def render_page_content():
    """Render the current page content based on navigation state."""
    current_page = get_current_page()
    
    # Page routing
    if current_page == "chat":
        render_chat_page()
    elif current_page == "library":
        render_library_page()
    elif current_page == "upload":
        render_upload_page()
    elif current_page == "settings":
        render_settings_page()
    else:
        # Fallback to chat
        render_chat_page()


def main():
    """Main application entry point."""
    
    # Initialize session state
    init_session_state()
    
    # Load custom CSS
    load_custom_css()
    
    # Check API connection
    connected, api = check_api_connection()
    
    # Render sidebar (always visible)
    render_sidebar()
    
    # Main content area
    if not connected:
        render_disconnected_state()
        return
    
    # Render top navbar
    render_navbar()
    
    # Render current page content
    render_page_content()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"Application error: {str(e)}")