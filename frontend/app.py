"""
RAG Chatbot Frontend - Streamlit UI with improved error handling and configuration.
"""

import streamlit as st
import requests
import os
import time
from typing import List, Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from components.process_flow import (
    render_process_flow,
    initialize_process_flow,
    update_process_status,
    get_process_flow
)
from components.system_info import (
    render_system_info,
    render_api_services
)
from components.enhancements import (
    render_enhanced_sources,
    render_enhanced_chat_message,
    render_error_state,
    render_success_state,
    render_info_state,
    render_organized_sidebar,
    render_theme_selector,
    render_dashboard_metrics,
    render_response_quality,
    render_session_stats,
    render_feedback_form
)

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8001")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

st.set_page_config(
    page_title="RAG Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=60)
def check_api_with_retry() -> bool:
    """
    Check API availability with retry logic.
    
    Returns:
        True if API is available, False otherwise
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
            continue
    return False


def check_api() -> bool:
    """Quick API check."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def upload_files(files: List) -> Dict[str, Any]:
    """
    Upload files to API with error handling.
    
    Args:
        files: List of uploaded files
        
    Returns:
        Response dictionary
    """
    if not files:
        return {"error": "No files provided"}
    
    try:
        file_data = []
        for f in files:
            if f is not None:
                file_data.append(("files", (f.name, f.getvalue(), f.type)))
        
        if not file_data:
            return {"error": "No valid files to upload"}
        
        response = requests.post(
            f"{API_URL}/upload",
            files=file_data,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Upload timeout. File may be too large."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Upload failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def query_rag(question: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Query RAG system with error handling.
    
    Args:
        question: Question to ask
        top_k: Number of context chunks
        
    Returns:
        Response dictionary
    """
    if not question or not question.strip():
        return {"answer": "Please enter a question.", "sources": []}
    
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"question": question.strip(), "top_k": top_k},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"answer": "Request timeout. The query may be too complex.", "sources": []}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return {"answer": "No documents loaded. Please upload documents first.", "sources": []}
        elif e.response.status_code == 503:
            return {"answer": "LLM service unavailable. Please check backend configuration.", "sources": []}
        else:
            return {"answer": f"Error: {e.response.text}", "sources": []}
    except requests.exceptions.RequestException as e:
        return {"answer": f"Connection error: {str(e)}", "sources": []}
    except Exception as e:
        return {"answer": f"Unexpected error: {str(e)}", "sources": []}


def generate_suggested_questions(num_questions: int = 5) -> Dict[str, Any]:
    """
    Call the backend to generate suggested questions.

    Args:
        num_questions: Number of questions to request

    Returns:
        Response dictionary
    """
    try:
        response = requests.post(
            f"{API_URL}/quiz",
            json={"num_questions": num_questions},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Suggested questions generation timeout."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            return {"error": "No documents loaded. Please upload documents first."}
        elif e.response.status_code == 503:
            return {"error": "LLM service unavailable. Please check backend configuration."}
        else:
            return {"error": f"Error: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def get_document_count() -> int:
    """Get document count from API."""
    try:
        response = requests.get(f"{API_URL}/documents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("chunks", 0)
    except:
        pass
    return 0


def clear_documents() -> bool:
    """Clear all documents."""
    try:
        response = requests.delete(f"{API_URL}/clear", timeout=10)
        return response.status_code == 200
    except:
        return False


# Initialize session state FIRST (before any sidebar operations)
if "history" not in st.session_state:
    st.session_state.history = []
if "last_upload_result" not in st.session_state:
    st.session_state.last_upload_result = None
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []

# Initialize smart process flow
if "smart_flow" not in st.session_state:
    st.session_state.smart_flow = {
        "select_docs": {"status": "pending", "desc": "Select documents"},
        "upload": {"status": "pending", "desc": "Upload documents"},  
        "chunk": {"status": "pending", "desc": "Processing & chunking"},
        "index": {"status": "pending", "desc": "Indexing complete"},
        "gen_questions": {"status": "pending", "desc": "Generate questions"},
        "ask_question": {"status": "pending", "desc": "Ask questions"},
        "get_answer": {"status": "pending", "desc": "Get AI answers"}
    }

# UI - Smart Process Flow
st.title("💬 RAG Chatbot")
st.markdown("**Smart Process Flow** - Follow the steps below:")

# Render smart flow
flow_items = []
for key, item in st.session_state.smart_flow.items():
    status = item["status"]
    icon = "⏳" if status == "pending" else "✅" if status == "success" else "🔄" if status == "processing" else "❌"
    flow_items.append(f"{icon} {item['desc']}")

st.markdown(" → ".join(flow_items))

# System Configuration Information
st.markdown("---")
render_system_info()
render_api_services()
st.markdown("---")

# API Status
api_status = check_api_with_retry()
if not api_status:
    st.error("⚠️ Cannot connect to API")
    st.info(f"**API URL:** {API_URL}")
    st.info("**To start the backend:**")
    st.code("cd backend && python main.py", language="bash")
    st.stop()
else:
    st.success("✅ Connected to API")

# Enhanced Sidebar with Organized Tabs
sidebar_data = render_organized_sidebar()

# Handle generate questions from sidebar
if st.session_state.get("generate_questions", False):
    st.session_state.generate_questions = False
    with st.spinner("🧠 Generating suggested questions..."):
        num_questions = sidebar_data.get("num_questions", 5)
        questions_result = generate_suggested_questions(num_questions)
        if "error" in questions_result:
            render_error_state(questions_result["error"], "validation")
        else:
            st.session_state.suggested_questions = questions_result.get("questions", [])
            st.success(f"✅ Generated {len(st.session_state.suggested_questions)} questions!")

# Handle uploads from sidebar (automatic when files selected)
uploaded_files = sidebar_data.get("uploaded_files", [])
if uploaded_files and (sidebar_data.get("auto_upload", False) or st.session_state.get("upload_btn", False)):
    # Update smart flow
    st.session_state.smart_flow["select_docs"]["status"] = "success"
    st.session_state.smart_flow["upload"]["status"] = "processing"
    st.session_state.smart_flow["chunk"]["status"] = "processing"
    
    update_process_status("Upload", "processing")
    with st.spinner("📤 Uploading and processing files..."):
        result = upload_files(uploaded_files)
        if "results" in result:
            st.session_state.last_upload_result = result
            
            # Update smart flow - upload and chunking complete
            st.session_state.smart_flow["upload"]["status"] = "success"
            st.session_state.smart_flow["chunk"]["status"] = "success"  
            st.session_state.smart_flow["index"]["status"] = "success"
            
            update_process_status("Upload", "success")
            update_process_status("Process", "success")
            update_process_status("Index", "success")
            update_process_status("Ready", "success")
            
            total_chunks = result.get('total_chunks', 0)
            render_success_state(f"✅ Uploaded {len(result['results'])} file(s)")
            st.write(f"**Total chunks:** {total_chunks}")
            
            # Update flow description with chunk count
            st.session_state.smart_flow["chunk"]["desc"] = f"Chunking complete ({total_chunks} chunks)"
            
            # Show individual results with enhanced styling
            for file_result in result.get("results", []):
                if file_result.get("status") == "ok":
                    st.markdown(f"### ✓ {file_result.get('filename')}")
                    
                    patterns = file_result.get("patterns") or []
                    chunking = file_result.get("chunking") or {}
                    
                    if patterns:
                        pattern_str = " | ".join(p.capitalize() for p in patterns)
                        render_info_state(f"📊 **Detected Data Patterns**: {pattern_str}")
                    
                    st.markdown(f"**Chunks Created**: {file_result.get('chunks', 0)}")
                    
                    if chunking:
                        st.markdown("**Chunking Strategies Applied:**")
                        for p_type, desc in chunking.items():
                            st.markdown(f"- **{p_type.capitalize()}**: {desc}")
                    
                    st.divider()
                else:
                    render_error_state(f"{file_result.get('filename')}: {file_result.get('msg', 'Error')}", "validation")
                    update_process_status("Upload", "error")
        elif "error" in result:
            render_error_state(result['error'], "connection")
            update_process_status("Upload", "error")
        else:
            render_error_state("Unknown error occurred", "general")
            update_process_status("Upload", "error")
    
    st.divider()
    
    # Document count
    if api_status:
        try:
            doc_count = get_document_count()
            st.metric("Document Chunks", doc_count)
        except:
            st.info("Chunks: Unable to fetch")
    else:
        st.info("Chunks: 0 (Backend not connected)")
    
    # Clear documents button
    if st.button("🗑️ Clear All Documents", use_container_width=True):
        if api_status:
            if clear_documents():
                # Clear session state
                st.session_state.suggested_questions = []
                st.session_state.history = []
                st.session_state.last_upload_result = None
                initialize_process_flow(["Upload", "Process", "Index", "Ready"])
                st.success("✅ Documents cleared")
                st.rerun()
            else:
                st.error("Failed to clear documents")
        else:
            st.warning("Backend not connected")

# Dashboard Metrics (NEW)
st.markdown("---")
st.subheader("📊 Session Overview")
render_session_stats()
st.markdown("---")

# Generate Questions Section (PROMINENT)
if api_status:
    try:
        doc_count = get_document_count()
        if doc_count > 0:
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.markdown("### 🧠 Generate Smart Questions")
                st.markdown("Get AI-suggested questions based on your uploaded documents")
            with col2:
                if st.button("✨ Generate Questions", use_container_width=True, type="primary"):
                    st.session_state.smart_flow["gen_questions"]["status"] = "processing"
                    
                    # Generate questions and store them
                    try:
                        with st.spinner("🎯 Generating intelligent questions..."):
                            response = requests.post("http://localhost:8000/quiz?num_questions=6&include_comparative=true", 
                                                   timeout=30)
                            if response.status_code == 200:
                                questions_data = response.json()
                                questions = questions_data.get("questions", [])
                            else:
                                questions = []
                        
                        if questions:
                            st.session_state.suggested_questions = questions
                            st.session_state.smart_flow["gen_questions"]["status"] = "success"
                        else:
                            st.session_state.smart_flow["gen_questions"]["status"] = "error"
                    except Exception as e:
                        st.error(f"❌ Error generating questions: {str(e)}")
                        st.session_state.smart_flow["gen_questions"]["status"] = "error"
                    
                    st.rerun()
    except:
        pass

# Chat Interface with Enhanced Features
col_title, col_stats = st.columns([0.85, 0.15])
with col_title:
    st.header("💭 Ask a Question")
with col_stats:
    if st.button("🗑️ Clear", use_container_width=True, help="Clear chat history", key="clear_chat"):
        st.session_state.history = []
        render_success_state("✅ Chat cleared")
        st.rerun()

# Display chat history with enhanced styling
if st.session_state.history:
    for idx, msg in enumerate(st.session_state.history):
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["text"])
        else:
            # Enhanced assistant message with sources and actions
            with st.chat_message("assistant"):
                st.write(msg["text"])
                
                sources = msg.get("sources", [])
                
                # Show response quality indicator if sources available
                if sources:
                    avg_similarity = sum(s.get("similarity", 0) for s in sources) / len(sources)
                    render_response_quality(sources, avg_similarity)
                
                # Enhanced sources display
                if sources and sidebar_data.get("show_sources", True):
                    st.divider()
                    render_enhanced_sources(sources)
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("👍", key=f"helpful_{idx}", help="Helpful"):
                        render_success_state("Thanks for the feedback!")
                with col2:
                    if st.button("👎", key=f"unhelpful_{idx}", help="Not helpful"):
                        render_info_state("We'll work on improving this!")
                with col3:
                    if st.button("📋", key=f"copy_{idx}", help="Copy"):
                        st.code(msg["text"])
                with col4:
                    if st.button("🔄", key=f"regen_{idx}", help="Regenerate"):
                        st.info("Regeneration request sent!")

# Input
question = st.chat_input("Ask a question about your documents...")

if question:
    # Add user message to history
    st.session_state.history.append({"role": "user", "text": question})
    
    # Display user message
    with st.chat_message("user"):
        st.write(question)
    
    # Get response with error handling
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            top_k = sidebar_data.get("top_k", 5)
            result = query_rag(question, top_k)
            answer = result.get("answer", "Error: No answer received")
            sources = result.get("sources", [])
            
            # Check for errors
            if "error" in result or "No documents" in answer or "unavailable" in answer.lower():
                render_error_state(answer, "validation")
            else:
                st.write(answer)
                
                # Show quality metrics
                if sources:
                    avg_similarity = sum(s.get("similarity", 0) for s in sources) / len(sources)
                    render_response_quality(sources, avg_similarity)
                    
                    # Enhanced sources display
                    if sidebar_data.get("show_sources", True):
                        st.divider()
                        render_enhanced_sources(sources)
    
    # Add assistant message to history
    st.session_state.history.append({
        "role": "bot",
        "text": answer,
        "sources": sources
    })
    
    # Update session stats
    if "session_stats" not in st.session_state:
        st.session_state.session_stats = {"questions_asked": 0, "total_response_time": 0, "start_time": time.time()}
    st.session_state.session_stats["questions_asked"] += 1

# Display Suggested Questions (if generated) - PROFESSIONAL SECTION
if st.session_state.get("suggested_questions"):
    st.markdown("---")
    
    # Professional header
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("<h2 style='margin: 0;'>💡 Suggested Questions</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p style='text-align: right; opacity: 0.7; margin: 0;'>{len(st.session_state.get('suggested_questions', []))} questions</p>", unsafe_allow_html=True)
    
    st.markdown("<p style='opacity: 0.6; margin: 10px 0 20px 0;'>Click any question below to instantly get an answer</p>", unsafe_allow_html=True)
    
    quiz_questions = st.session_state.suggested_questions
    
    # Create a clean, professional grid
    for idx, q in enumerate(quiz_questions, 1):
        if isinstance(q, dict):
            question_text = q.get('question', '')
            q_type = q.get('type', 'comparative')
        else:
            question_text = str(q)
            q_type = 'comparative'
        
        # Determine styling based on type
        if q_type == 'comparative':
            icon = "🔀"
            accent_color = "#667eea"
        else:
            icon = "🎯"
            accent_color = "#764ba2"
        
        # Professional question card with minimal design
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #e0e0e0;
            border-left: 4px solid {accent_color};
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            transition: all 0.2s ease;
        ">
            <div style="display: flex; align-items: flex-start; gap: 12px;">
                <span style="font-size: 20px; flex-shrink: 0;">{icon}</span>
                <div style="flex: 1;">
                    <div style="color: #2c3e50; font-weight: 500; line-height: 1.5; margin-bottom: 8px;">
                        {question_text}
                    </div>
                    <div style="font-size: 12px; opacity: 0.5;">
                        Question {idx} of {len(quiz_questions)}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Single, clear call-to-action button
        col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
        with col2:
            if st.button(
                f"Ask Question",
                key=f"use_q_{idx}",
                use_container_width=True,
            ):
                # Update smart flow
                st.session_state.smart_flow["ask_question"]["status"] = "processing"
                
                # Add user message
                st.session_state.history.append({"role": "user", "text": question_text})
                
                # Auto-generate answer
                with st.spinner("🔄 Generating answer..."):
                    top_k = sidebar_data.get("top_k", 5)
                    result = query_rag(question_text, top_k)
                    answer = result.get("answer", "Error: No answer received")
                    sources = result.get("sources", [])
                    
                    # Add assistant message
                    st.session_state.history.append({
                        "role": "bot", 
                        "text": answer, 
                        "sources": sources
                    })
                    
                    # Update flow status
                    st.session_state.smart_flow["ask_question"]["status"] = "success"
                    st.session_state.smart_flow["get_answer"]["status"] = "success"
                
                st.rerun()

# Theme Selector in Sidebar (NEW)
theme = render_theme_selector()

# Footer with Enhanced Styling
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; margin-top: 20px;">
    <small>
    <strong>RAG Chatbot</strong> • Powered by FAISS, Sentence Transformers, and Groq<br>
    <a href="#" style="text-decoration: none; color: #667eea;">📧 Feedback</a> • 
    <a href="#" style="text-decoration: none; color: #667eea;">💡 Suggestions</a> • 
    <a href="#" style="text-decoration: none; color: #667eea;">🐛 Report Bug</a>
    </small>
</div>
""", unsafe_allow_html=True)
