# RAG Chatbot - Minimal Frontend
import streamlit as st
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import API_URL, REQUEST_TIMEOUT, PAGE_TITLE, PAGE_ICON
from utils.api_client import get_api_client
from components.chat import render_chat_interface
from components.documents import render_upload_section, render_document_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

if "api_connected" not in st.session_state:
    st.session_state.api_connected = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

def check_api():
    try:
        api = get_api_client(API_URL, REQUEST_TIMEOUT)
        st.session_state.api_connected = api.health_check()
        return st.session_state.api_connected, api
    except:
        st.session_state.api_connected = False
        return False, None

def main():
    # Header
    st.title("🤖 RAG Chatbot")
    
    # Check API connection
    connected, api = check_api()
    
    if not connected:
        st.error(f"❌ Cannot connect to API at {API_URL}")
        st.info("💡 Start backend: `cd backend && python main.py`")
        return
    
    # Get document stats
    try:
        docs = api.get_documents()
        total_chunks = docs.get("total_chunks", 0)
        total_docs = len(docs.get("documents", []))
        
        # Status bar
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.success("✅ Connected to backend")
        with col2:
            st.metric("Documents", total_docs)
        with col3:
            st.metric("Chunks", total_chunks)
            
        st.divider()
        
        # Main content
        if total_chunks == 0:
            # No documents - show upload
            st.warning("📂 No documents uploaded yet")
            st.markdown("### Upload Documents")
            render_upload_section(api)
        else:
            # Documents available - show chat with option to upload more
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("### 💬 Chat")
                render_chat_interface(api, {"TOP_K": 5})
            
            with col2:
                st.markdown("### 📚 Library")
                render_document_stats(api)
                st.markdown("### ➕ Add More")
                render_upload_section(api)
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
        st.error(f"Application error: {str(e)}")