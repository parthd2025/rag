import streamlit as st
import logging
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import API_URL, REQUEST_TIMEOUT, PAGE_TITLE, PAGE_ICON
from utils.api_client import get_api_client
from utils.ui_components import render_custom_css
from components.chat import render_chat_interface
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
    st.markdown("# 🤖 RAG Chatbot")
    st.markdown("Upload documents • Ask questions • Learn")
    
    connected, api = check_api()
    
    if not connected:
        st.error(f"Cannot connect to {API_URL}")
        st.info("Start backend: `cd backend && python main.py`")
        return
    
    try:
        docs_info = api.get_documents()
        chunks = docs_info.get("total_chunks", 0)
        num_docs = len(docs_info.get("documents", []))
    except:
        chunks = 0
        num_docs = 0
    
    # Status
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "✅ Online")
    col2.metric("Documents", num_docs)
    col3.metric("Chunks", chunks)
    
    st.divider()
    
    # Upload Section
    st.markdown("## 📤 Upload")
    col1, col2 = st.columns([2, 1])
    with col1:
        render_upload_section(api)
    with col2:
        render_document_stats(api)
    
    st.divider()
    
    if chunks > 0:
        # Chat Section
        st.markdown("## 💬 Chat")
        render_chat_interface(api, {"TOP_K": 5})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
        with col2:
            if st.button("💾 Export", use_container_width=True):
                st.download_button("Download", json.dumps(st.session_state.chat_messages), "chat.json")
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        st.divider()
        
        # Quiz Section
        st.markdown("## 🎯 Quiz")
        if st.session_state.get("quiz_active"):
            render_quiz_mode(api)
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                num_q = st.slider("Questions:", 1, 20, 5)
            with col2:
                if st.button("Generate", use_container_width=True):
                    with st.spinner("Creating..."):
                        try:
                            quiz = api.generate_quiz(num_q)
                            st.session_state.quiz_active = True
                            st.session_state.quiz_data = quiz
                            st.session_state.quiz_answers = {}
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
        
        st.divider()
        
        # System & Help
        st.markdown("## ⚙️ Info")
        col1, col2 = st.columns([1, 1])
        with col1:
            render_system_dashboard(api)
        with col2:
            render_help_section()
    else:
        st.info("👆 Upload documents above to start")
    
    st.divider()
    
    # Delete Section
    st.markdown("## 🗑️ Delete")
    if st.button("Clear All", use_container_width=True):
        if st.checkbox("Confirm"):
            try:
                api.clear_data()
                st.success("Cleared!")
                st.rerun()
            except Exception as e:
                st.error(str(e))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
        st.error(f"Error: {str(e)}")
