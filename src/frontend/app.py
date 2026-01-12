# RAG Chatbot - Minimal Frontend
import streamlit as st
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import API_URL, REQUEST_TIMEOUT, PAGE_TITLE, PAGE_ICON
from utils.api_client import get_api_client
from components.chat import render_chat_interface
from components.documents import render_upload_section, render_document_stats, render_document_management
from components.settings import render_settings_dashboard, render_quick_settings_panel

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
        total_chunks = docs.get("chunks", 0)  # Backend uses "chunks" not "total_chunks"
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
        
        # Always show the interface with both upload and chat capabilities
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📚 Library", "⚙️ Settings"])
        
        with tab1:
            # Show chat interface with guidance based on document availability
            if total_chunks == 0:
                st.info("📝 **No documents processed yet.** Upload documents in the 'Library' tab to start asking questions!")
                st.markdown("### 🤖 Ready to Chat")
                st.markdown("*Upload some documents first, then come back here to ask questions about them.*")
            else:
                st.success(f"📚 **{total_chunks} chunks ready** from {total_docs} document(s). Ask me anything!")
            
            # Always render the chat interface (it handles the empty state internally)
            render_chat_interface(api, {"TOP_K": 5})
        
        with tab2:
            # Document management and upload
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if total_chunks > 0:
                    render_document_stats(api)
                else:
                    st.warning("📂 No documents uploaded yet")
                    # Tips for new users
                    with st.expander("💡 Getting Started Tips", expanded=True):
                        st.markdown("""
                        **📚 Supported Documents:**
                        - PDF files, Word documents, Text files
                        - CSV/Excel files, PowerPoint presentations
                        - HTML files and Markdown documents
                        
                        **🎯 Best Practices:**
                        - Upload multiple related documents for better insights
                        - Ensure documents are text-readable (not scanned images)
                        - Start with 2-5 documents to test the system
                        
                        **🚀 What You Can Do:**
                        - Ask questions about document content
                        - Compare information across documents
                        - Get summaries and key insights
                        - Generate follow-up questions
                        """)
                
            with col2:
                st.markdown("### 📤 Upload Your Documents")
                render_upload_section(api)
                
                st.markdown("### ⚙️ Quick Setup")
                render_quick_settings_panel(api)
            
            if total_chunks > 0:
                st.divider()
                render_document_management(api)
        
        with tab3:
            # Settings dashboard
            render_settings_dashboard(api)
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
        st.error(f"Application error: {str(e)}")