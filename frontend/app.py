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


def generate_quiz(num_questions: int = 5) -> Dict[str, Any]:
    """
    Call the backend to generate a quiz.

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
        return {"error": "Quiz generation timeout."}
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
if "quiz" not in st.session_state:
    st.session_state.quiz = []

# UI
st.title("💬 RAG Chatbot")
st.markdown("Ask questions about your uploaded documents using Retrieval-Augmented Generation.")

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

# Sidebar
with st.sidebar:
    st.header("📁 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "docx", "txt", "md", "csv", "xlsx", "xls", "pptx", "html", "htm", "xml", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="Upload documents in various formats"
    )
    
    if st.button("Upload", type="primary", use_container_width=True):
        if uploaded_files:
            with st.spinner("Processing files..."):
                result = upload_files(uploaded_files)
                if "results" in result:
                    st.session_state.last_upload_result = result  # Store in session state
                    st.success(f"✅ Uploaded {len(result['results'])} file(s)")
                    st.write(f"**Total chunks:** {result.get('total_chunks', 0)}")
                    
                    # Show individual results with pattern info at the top
                    for file_result in result.get("results", []):
                        if file_result.get("status") == "ok":
                            st.markdown(f"### ✓ {file_result.get('filename')}")
                            
                            # Display patterns prominently
                            patterns = file_result.get("patterns") or []
                            chunking = file_result.get("chunking") or {}
                            
                            if patterns:
                                pattern_str = " | ".join(p.capitalize() for p in patterns)
                                st.info(f"📊 **Detected Data Patterns**: {pattern_str}")
                            
                            # Display file stats
                            st.markdown(f"**Chunks Created**: {file_result.get('chunks', 0)}")
                            
                            # Display chunking strategies used
                            if chunking:
                                st.markdown("**Chunking Strategies Applied:**")
                                for p_type, desc in chunking.items():
                                    st.markdown(f"- **{p_type.capitalize()}**: {desc}")
                            
                            st.divider()
                        else:
                            st.warning(f"  ✗ {file_result.get('filename')}: {file_result.get('msg', 'Error')}")
                elif "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    st.error("Unknown error occurred")
        else:
            st.warning("Please select files to upload")
    
    # Display stored upload results even after slider changes
    if st.session_state.last_upload_result and not uploaded_files:
        result = st.session_state.last_upload_result
        st.divider()
        st.info("📋 **Last Upload Summary**")
        st.write(f"**Total chunks:** {result.get('total_chunks', 0)}")
        
        for file_result in result.get("results", []):
            if file_result.get("status") == "ok":
                st.markdown(f"#### ✓ {file_result.get('filename')}")
                
                patterns = file_result.get("patterns") or []
                chunking = file_result.get("chunking") or {}
                
                if patterns:
                    pattern_str = " | ".join(p.capitalize() for p in patterns)
                    st.info(f"📊 **Detected Data Patterns**: {pattern_str}")
                
                st.markdown(f"**Chunks Created**: {file_result.get('chunks', 0)}")
                
                if chunking:
                    st.markdown("**Chunking Strategies Applied:**")
                    for p_type, desc in chunking.items():
                        st.markdown(f"- **{p_type.capitalize()}**: {desc}")
    
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
    
    # Clear button
    if st.button("🗑️ Clear All Documents", use_container_width=True):
        if api_status:
            if clear_documents():
                st.success("✅ Documents cleared")
                st.rerun()
            else:
                st.error("Failed to clear documents")
        else:
            st.warning("Backend not connected")
    
    st.divider()
    
    # Settings
    st.header("⚙️ Settings")
    top_k = st.slider(
        "Context Chunks",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of document chunks to use as context"
    )

    st.divider()

    # Quiz controls
    st.header("📝 Quiz")
    num_questions = st.slider(
        "Number of quiz questions",
        min_value=1,
        max_value=10,
        value=5,
        help="How many quiz questions to generate from the documents",
    )
    if st.button("Generate Quiz", use_container_width=True):
        with st.spinner("Generating quiz..."):
            quiz_result = generate_quiz(num_questions)
            if "error" in quiz_result:
                st.error(quiz_result["error"])
            else:
                st.session_state.quiz = quiz_result.get("questions", [])

# Chat Interface
st.header("💭 Ask a Question")

# Display chat history
if st.session_state.history:
    for msg in st.session_state.history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["text"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["text"])
                if msg.get("sources"):
                    with st.expander("📚 Sources", expanded=False):
                        for i, src in enumerate(msg["sources"][:5], 1):
                            similarity = src.get("similarity", 0)
                            st.markdown(f"**Source {i}** (similarity: {similarity:.2%})")
                            chunk_preview = src.get("chunk", "")[:200]
                            st.text(chunk_preview + ("..." if len(src.get("chunk", "")) > 200 else ""))

# Input
question = st.chat_input("Ask a question about your documents...")

if question:
    # Add user message to history
    st.session_state.history.append({"role": "user", "text": question})
    
    # Display user message
    with st.chat_message("user"):
        st.write(question)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = query_rag(question, top_k)
            answer = result.get("answer", "Error: No answer received")
            sources = result.get("sources", [])
            
            st.write(answer)
            
            if sources:
                with st.expander("📚 Sources", expanded=False):
                    for i, src in enumerate(sources[:5], 1):
                        similarity = src.get("similarity", 0)
                        st.markdown(f"**Source {i}** (similarity: {similarity:.2%})")
                        chunk_preview = src.get("chunk", "")[:200]
                        st.text(chunk_preview + ("..." if len(src.get("chunk", "")) > 200 else ""))
    
    # Add assistant message to history
    st.session_state.history.append({
        "role": "bot",
        "text": answer,
        "sources": sources
    })

# Quiz display (if any)
if "quiz" in st.session_state and st.session_state.quiz:
    st.header("📝 Generated Quiz")
    quiz_questions = st.session_state.quiz

    st.subheader("Question List")
    for idx, q in enumerate(quiz_questions):
        st.markdown(f"{idx + 1}. {q.get('question', '')}")

# Footer
st.divider()
st.markdown(
    "<small>RAG Chatbot - Powered by FAISS, Sentence Transformers, and Groq</small>",
    unsafe_allow_html=True
)
