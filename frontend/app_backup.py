# RAG Chatbot - Simplified Frontend
import streamlit as st
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import API_URL, REQUEST_TIMEOUT, PAGE_TITLE, PAGE_ICON
from utils.api_client import get_api_client
from utils.ui_components import render_custom_css, success_alert, error_alert, info_alert
from components.chat import render_chat_interface, render_quick_actions
from components.documents import render_upload_section, render_document_stats, render_clear_section
from components.quiz import render_quiz_interface, render_quiz_mode
from components.system_info import render_system_dashboard, render_help_section

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")

if "api_connected" not in st.session_state:
    st.session_state.api_connected = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

render_custom_css()

def check_api():
    try:
        api = get_api_client(API_URL, REQUEST_TIMEOUT)
        st.session_state.api_connected = api.health_check()
        return st.session_state.api_connected, api
    except:
        st.session_state.api_connected = False
        return False, None

def main():
    st.markdown("# RAG Chatbot - Simple & Fast")
    st.markdown("*Ask questions about your documents*")
    st.divider()
    
    connected, api = check_api()
    
    if not connected:
        st.error(f"Cannot connect to API at {API_URL}")
        st.info("Start backend: cd backend && python main.py")
        return
    
    st.success("Connected to backend")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Chat", "Upload", "Quiz", "Settings"])
    
    st.sidebar.divider()
    
    try:
        docs = api.get_documents()
        st.sidebar.metric("Chunks", docs.get("total_chunks", 0))
        st.sidebar.metric("Docs", len(docs.get("documents", [])))
    except:
        pass
    
    st.divider()
    
    # Routes
    if page == "Chat":
        render_chat(api)
    elif page == "Upload":
        render_upload(api)
    elif page == "Quiz":
        render_quiz(api)
    else:
        render_settings(api)

def render_chat(api):
    st.markdown("## Chat")
    try:
        docs = api.get_documents()
        if not docs or docs.get("total_chunks", 0) == 0:
            st.warning("No documents uploaded. Go to Upload first.")
            return
        render_chat_interface(api, {"TOP_K": 5})
        st.divider()
        render_quick_actions(api)
    except Exception as e:
        st.error(str(e))

def render_upload(api):
    st.markdown("## Upload Documents")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown("### Add Document")
        render_upload_section(api)
    with col2:
        st.markdown("### Library")
        render_document_stats(api)
    st.divider()
    st.markdown("### Data Management")
    render_clear_section(api)

def render_quiz(api):
    st.markdown("## Take Quiz")
    try:
        docs = api.get_documents()
        if not docs or docs.get("total_chunks", 0) == 0:
            st.warning("No documents. Please upload first.")
            return
        if st.session_state.get("quiz_active"):
            render_quiz_mode(api)
        else:
            render_quiz_interface(api)
    except Exception as e:
        st.error(str(e))

def render_settings(api):
    st.markdown("## Settings")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### System")
        render_system_dashboard(api)
    with col2:
        st.markdown("### Help")
        render_help_section()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
        st.error(f"Error: {str(e)}")
