import streamlit as st
import requests
import logging
from typing import Any, Dict, List, Tuple
from urllib.parse import quote

from config import (
    API_URL as CONFIG_API_URL,
    REQUEST_TIMEOUT as CONFIG_REQUEST_TIMEOUT,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
)


logger = logging.getLogger(__name__)

API_URL = (CONFIG_API_URL or "http://localhost:8001").rstrip("/")
REQUEST_TIMEOUT = int(CONFIG_REQUEST_TIMEOUT) if CONFIG_REQUEST_TIMEOUT else 120
HEALTH_CHECK_TIMEOUT = 5
DEFAULT_CHAT_TOP_K = 5


st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=(LAYOUT if LAYOUT else "wide"),
)


def _response_detail(response: requests.Response) -> str:
    """Extract a readable error message from a failed HTTP response."""
    try:
        data = response.json()
    except ValueError:
        return response.text or "Unexpected response error."

    if isinstance(data, dict):
        for key in ("detail", "message", "error"):
            if key in data and data[key]:
                return str(data[key])
    return str(data)


def check_api() -> bool:
    """Ping backend health endpoint and update connection state."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=HEALTH_CHECK_TIMEOUT)
        response.raise_for_status()
        st.session_state["api_connected"] = True
        return True
    except Exception as exc:
        logger.warning(f"Health check failed: {exc}")
        st.session_state["api_connected"] = False
        return False


def get_stats() -> Tuple[List[Dict[str, Any]], int, int]:
    """Retrieve document inventory and chunk totals."""
    try:
        response = requests.get(f"{API_URL}/documents", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        logger.error(f"Failed to fetch document stats: {exc}")
        return [], 0, 0

    documents = data.get("documents") or []
    total_chunks = data.get("chunks") or data.get("total_chunks") or 0
    total_docs = data.get("total_documents") or data.get("total_count") or len(documents)
    return documents, total_chunks, total_docs


def upload_files(files) -> Dict[str, Any]:
    """Upload one or more files to the backend."""
    if not files:
        return {"results": []}

    payload = []
    for f in files:
        content = f.getvalue()
        payload.append(("files", (f.name, content, f.type or "application/octet-stream")))

    try:
        response = requests.post(f"{API_URL}/upload", files=payload, timeout=REQUEST_TIMEOUT)
    except Exception as exc:
        logger.error(f"Upload request failed: {exc}")
        raise RuntimeError(str(exc)) from exc

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(_response_detail(response)) from exc

    return response.json()


def reload_vector_store() -> Dict[str, Any]:
    """Request backend to reload vector store from disk."""
    try:
        response = requests.post(f"{API_URL}/documents/reload", timeout=REQUEST_TIMEOUT)
    except Exception as exc:
        logger.error(f"Reload request failed: {exc}")
        raise RuntimeError(str(exc)) from exc

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(_response_detail(response)) from exc

    return response.json()


def delete_document(document_name: str) -> bool:
    """Delete a single document if the backend supports it."""
    encoded = quote(document_name, safe="")
    try:
        response = requests.delete(f"{API_URL}/documents/{encoded}", timeout=REQUEST_TIMEOUT)
    except Exception as exc:
        logger.error(f"Delete request failed for {document_name}: {exc}")
        raise RuntimeError(str(exc)) from exc

    if response.status_code == 404:
        raise RuntimeError(f"Document '{document_name}' not found in vector store.")
    if response.status_code == 405:
        raise RuntimeError("Backend does not support document deletion.")

    try:
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(_response_detail(response)) from exc


def ask_question(question: str, *, top_k: int = DEFAULT_CHAT_TOP_K) -> Dict[str, Any]:
    """Send a question to the chat endpoint."""
    payload = {"question": question, "top_k": top_k}

    try:
        response = requests.post(f"{API_URL}/chat", json=payload, timeout=REQUEST_TIMEOUT)
    except Exception as exc:
        logger.error(f"Chat request failed: {exc}")
        raise RuntimeError(str(exc)) from exc

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(_response_detail(response)) from exc

    return response.json()


def clear_data() -> None:
    """Clear all documents from the backend."""
    try:
        response = requests.delete(f"{API_URL}/clear", timeout=REQUEST_TIMEOUT)
    except Exception as exc:
        logger.error(f"Clear request failed: {exc}")
        raise RuntimeError(str(exc)) from exc

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(_response_detail(response)) from exc


# Config
# Theme CSS (AI palette)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0F0F23 0%, #1A1A2E 50%, #16213E 100%);
        color: #FFFFFF;
    }

    .main .block-container {
        max-width: 1400px;
        padding: 2rem 3rem 4rem;
    }

    [data-testid="stSidebar"] { display: none; }

    h1, h2, h3, h4 { color: #FFFFFF !important; font-weight: 700; }
    p, span, label { color: #B8B8CC !important; }
    h1 { background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

    .status-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    }
    .status-label { color: #B8B8CC !important; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
    .status-value { color: #FFFFFF !important; font-size: 28px; font-weight: 700; }
    .status-online { color: #4ECDC4 !important; }

    .upload-zone {
        background: rgba(255,255,255,0.05);
        border: 2px dashed rgba(103,126,234,0.4);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin: 10px 0;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    .upload-zone:hover { border-color: #667EEA; background: rgba(103,126,234,0.1); transform: translateY(-2px); }

    .stButton > button {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(103,126,234,0.4);
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(103,126,234,0.6);
        background: linear-gradient(135deg, #764BA2 0%, #667EEA 100%);
    }

    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.05);
        border: 2px dashed rgba(103,126,234,0.4);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #667EEA;
        background: rgba(103,126,234,0.1);
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px;
        color: #FFFFFF !important;
        padding: 12px 16px;
        backdrop-filter: blur(10px);
    }
    .stTextInput > div > div > input:focus {
        border-color: #667EEA !important;
        box-shadow: 0 0 0 2px rgba(103,126,234,0.3);
        background: rgba(255,255,255,0.15) !important;
    }

    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 24px !important; font-weight: 700 !important; }
    [data-testid="stMetricLabel"] { color: #B8B8CC !important; }

    .user-msg {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: #FFFFFF;
        padding: 16px 20px;
        border-radius: 20px 20px 6px 20px;
        margin: 8px 0;
        box-shadow: 0 4px 15px rgba(103,126,234,0.3);
    }
    .bot-msg {
        background: rgba(255,255,255,0.1);
        color: #FFFFFF;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 6px;
        margin: 8px 0;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .info-box {
        background: rgba(76,205,196,0.15);
        border-left: 4px solid #4ECDC4;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        color: #4ECDC4 !important;
        backdrop-filter: blur(10px);
    }
    .success-box {
        background: rgba(76,205,196,0.15);
        border-left: 4px solid #4ECDC4;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        color: #4ECDC4 !important;
        backdrop-filter: blur(10px);
    }
    .error-box {
        background: rgba(255,107,107,0.15);
        border-left: 4px solid #FF6B6B;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        color: #FF6B6B !important;
        backdrop-filter: blur(10px);
    }

    hr { border-color: rgba(255,255,255,0.2) !important; margin: 20px 0 !important; }

    .file-item {
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        color: #FFFFFF;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.2s ease;
    }
    .file-item:hover {
        background: rgba(255,255,255,0.15);
        transform: translateX(4px);
    }

    .section-header {
        color: #667EEA !important;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 16px;
        letter-spacing: 0.02em;
    }

    .source-ref {
        background: rgba(176,183,193,0.2);
        border-left: 3px solid #B0B7C1;
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 0 6px 6px 0;
    }
    .source-doc { color: #423630 !important; font-weight: 500; }
    .source-page { color: #967E71 !important; }
    .source-similarity { color: #423630 !important; }
    .source-preview { color: #967E71 !important; font-style: italic; font-size: 12px; }

    .quiz-question {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        backdrop-filter: blur(20px);
    }
    .quiz-question-text {
        color: #FFFFFF !important;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 16px;
    }
    .quiz-btn {
        background: rgba(103,126,234,0.2);
        border: 1px solid rgba(103,126,234,0.4);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #FFFFFF !important;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .quiz-btn:hover { 
        background: rgba(103,126,234,0.3); 
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(103,126,234,0.3);
    }

    .quiz-answer {
        background: rgba(76,205,196,0.15);
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 12px;
        color: #FFFFFF;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(76,205,196,0.2);
    }

    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }

    .stSelectbox > div > div {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px;
        color: #FFFFFF !important;
        backdrop-filter: blur(10px);
    }
    .stNumberInput > div > div > input {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: #FFFFFF !important;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05);
        color: #B8B8CC;
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
    }
    .stTabs [data-baseweb="tab"]:hover { 
        color: #FFFFFF; 
        background: rgba(255,255,255,0.1);
    }
    .stTabs [data-baseweb="tab"]:focus { color: #FFFFFF; }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #667EEA !important;
        color: #FFFFFF !important;
        background: rgba(103,126,234,0.1) !important;
    }

    .stForm {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(20px);
    }
    .stSlider > div { color: #B8B8CC !important; }

    @media (max-width: 1200px) {
        .main .block-container {
            padding: 1.5rem 2rem 3rem;
        }
        .status-value { font-size: 24px; }
        .stButton > button { padding: 10px 20px; }
    }

    @media (max-width: 850px) {
        .main .block-container {
            max-width: 100%;
            padding: 1.25rem 1.25rem 2.5rem;
        }
        h1 { font-size: 2rem !important; }
        .status-value { font-size: 20px; }
        .status-label { font-size: 11px; }
        div[data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        .stButton > button {
            width: 100%;
            padding: 10px 16px;
        }
        .quiz-question {
            padding: 18px;
        }
        .user-msg, .bot-msg {
            padding: 14px 18px;
        }
    }

    @media (max-width: 600px) {
        .main .block-container {
            padding: 1rem 0.75rem 2rem;
        }
        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.4rem !important; }
        .status-value { font-size: 18px; }
        .stTextInput > div > div > input {
            padding: 10px 14px;
        }
        .bot-msg,
        .user-msg {
            font-size: 0.95rem;
            padding: 12px 16px;
        }
        .section-header {
            font-size: 18px ;
        }
    }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


if "api_connected" not in st.session_state:
    st.session_state.api_connected = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Session state initialization for suggested questions
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []


def generate_suggested_questions(num_questions=5):
    """Generate suggested questions from documents."""
    try:
        r = requests.post(
            f"{API_URL}/suggested-questions",
            json={"num_questions": num_questions},
            timeout=30,  # Reduced timeout for better performance
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except:
            detail = str(e)
        raise Exception(detail)
    except Exception as e:
        raise Exception(str(e))


def fetch_settings():
    """Retrieve current runtime settings."""
    try:
        response = requests.get(f"{API_URL}/config", timeout=min(10, REQUEST_TIMEOUT))
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as exc:
        logger.error(f"Failed to retrieve settings: {exc}")
        return None


def update_settings_api(payload):
    """Send settings update to backend."""
    try:
        response = requests.put(f"{API_URL}/settings", json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("settings", data)
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        raise Exception(detail)
    except Exception as e:
        raise Exception(str(e))


def main():
    # Check connection
    connected = check_api()
    settings_data = fetch_settings() if connected else None
    docs_list, chunks, total_docs = get_stats() if connected else ([], 0, 0)
    num_docs = total_docs if isinstance(total_docs, int) else (len(docs_list) if isinstance(docs_list, list) else 0)
    
    # ===== HEADER =====
    st.markdown("# 🤖 RAG Chatbot")
    st.markdown("*Upload documents • Ask questions • Learn*")
    
    # ===== STATUS BAR =====
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="status-label">Status</p>', unsafe_allow_html=True)
        if connected:
            st.markdown('<p class="status-value status-online">☑ Online</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-value" style="color:#ff4d4d">☒ Offline</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="status-label">Documents</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="status-value">{num_docs}</p>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<p class="status-label">Chunks</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="status-value">{chunks}</p>', unsafe_allow_html=True)
    
    st.divider()
    
    if not connected:
        st.markdown('<div class="error-box">⚠️ Cannot connect to backend. Start with: <code>cd backend && python main.py</code></div>', unsafe_allow_html=True)
        return
    
    if settings_data:
        st.markdown('<p class="section-header">⚙️ Settings</p>', unsafe_allow_html=True)
        default_chunking = int(settings_data.get("chunking_level", 5) or 5)
        default_context = int(settings_data.get("context_window_size", 2048) or 2048)
        default_top_k = int(settings_data.get("top_k", 5) or 5)
        default_temperature = float(settings_data.get("temperature", 0.7) or 0.7)

        with st.form("settings_form"):
            col_left, col_right = st.columns(2)
            with col_left:
                chunking_level = st.slider("Chunking Level", 1, 10, default_chunking,
                                          help="Document chunking strategy (1=simple, 10=advanced)")
                context_window = st.slider("Context Window (characters)", 256, 8192, default_context, 
                                          step=256, help="Maximum context length for RAG responses")
            with col_right:
                top_k = st.slider("Retrieval Top K", 1, 20, default_top_k,
                                help="Number of document chunks to retrieve")
                temperature = st.slider("LLM Temperature", 0.0, 1.0, default_temperature, 0.05,
                                      help="Answer creativity (0.0=focused, 1.0=creative)")

            submitted = st.form_submit_button("Save Settings", use_container_width=True)

        st.caption(
            f"Active chunk size: {settings_data.get('chunk_size', '—')} chars • Overlap: {settings_data.get('chunk_overlap', '—')} chars"
        )

        if submitted:
            payload = {}
            if chunking_level != default_chunking:
                payload["chunking_level"] = int(chunking_level)
            if context_window != default_context:
                payload["context_window_size"] = int(context_window)
            if top_k != default_top_k:
                payload["top_k"] = int(top_k)
            if abs(temperature - default_temperature) > 1e-6:
                payload["temperature"] = float(temperature)

            if payload:
                try:
                    update_settings_api(payload)
                    st.success("Settings updated successfully.")
                    st.experimental_rerun()
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ {e}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">No changes detected.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">Settings service unavailable.</div>', unsafe_allow_html=True)

    # ===== UPLOAD SECTION =====
    st.markdown('<p class="section-header">📤 Upload</p>', unsafe_allow_html=True)
    
    col_upload, col_stats = st.columns([3, 1])
    
    with col_upload:
        uploaded_files = st.file_uploader(
            "Drag and drop file here",
            type=["pdf", "docx", "txt", "md", "csv", "xlsx", "pptx", "html", "htm"],
            accept_multiple_files=True,
            help="Limit 200MB per file • PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML, HTM"
        )
        
        if uploaded_files:
            for f in uploaded_files:
                st.markdown(f'<div class="file-item">📄 {f.name} <span style="color:#888;margin-left:10px">{f.size/1024:.1f} KB</span></div>', unsafe_allow_html=True)
            
            if st.button("Upload", type="primary", use_container_width=True):
                with st.spinner(f"Uploading {len(uploaded_files)} file(s)..."):
                    try:
                        result = upload_files(uploaded_files)
                        for res in result.get("results", []):
                            if res.get("status") == "ok":
                                st.markdown(f'<div class="success-box">✅ {res.get("filename")} - {res.get("chunks", 0)} chunks</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="error-box">❌ {res.get("filename")}: {res.get("msg", "Error")}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="error-box">❌ Upload failed: {e}</div>', unsafe_allow_html=True)
                st.rerun()
    
    with col_stats:
        st.markdown('<p class="status-label">Chunks</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="status-value">{chunks}</p>', unsafe_allow_html=True)
        st.markdown('<p class="status-label">Docs</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="status-value">{num_docs}</p>', unsafe_allow_html=True)
        if st.button('↻ Reload Index', use_container_width=True):
            with st.spinner('Reloading vector store...'):
                try:
                    reload_vector_store()
                    st.success('Vector store reloaded successfully.')
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Reload failed: {e}</div>', unsafe_allow_html=True)
    
    # ===== DOCUMENT LIST =====
    if docs_list:
        st.markdown('<p class="section-header">📚 Documents</p>', unsafe_allow_html=True)
        for doc in docs_list:
            display_name = doc.get("name") or doc.get("title") or doc.get("source_doc") or "Unknown"
            doc_identifier = doc.get("source_doc") or display_name
            metadata_bits = []
            if doc.get("version"):
                metadata_bits.append(f"v{doc['version']}")
            if doc.get("ingested_at"):
                metadata_bits.append(doc.get("ingested_at"))
            if doc.get("tags"):
                tag_str = ", ".join(doc.get("tags"))
                if tag_str:
                    metadata_bits.append(tag_str)

            col_name, col_chunks, col_del = st.columns([4, 1, 1])
            with col_name:
                st.markdown(f'📄 {display_name}')
                if metadata_bits:
                    st.caption(" • ".join(metadata_bits))
                if doc.get("preview"):
                    st.caption(f"{doc['preview']}…")
            with col_chunks:
                st.caption(f'{doc.get("chunks", 0)} chunks')
            with col_del:
                if st.button("🗑️", key=f"del_{doc_identifier}", help=f"Delete {display_name}"):
                    with st.spinner("Removing document..."):
                        try:
                            success = delete_document(doc_identifier)
                            if success:
                                st.success(f"Document '{display_name}' deleted successfully")
                                st.rerun()
                        except Exception as e:
                            st.markdown(f'<div class="error-box">❌ Delete failed: {e}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # ===== CHAT SECTION =====
    if chunks == 0:
        st.markdown('<div class="info-box">👆 Upload documents above to start</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="section-header">💬 Ask a Question</p>', unsafe_allow_html=True)
        
        col_input, col_btn = st.columns([6, 1])
        
        with col_input:
            # Pre-fill with suggested question if clicked
            default_value = st.session_state.get("last_question", "")
            question = st.text_input("Question", placeholder="What would you like to know?", 
                                   label_visibility="collapsed", value=default_value)
            # Clear the suggested question after loading it
            if "last_question" in st.session_state:
                del st.session_state.last_question
        
        with col_btn:
            send = st.button("➤", use_container_width=True)
        
        if send and question.strip():
            with st.spinner("Thinking..."):
                try:
                    response = ask_question(question)
                    st.session_state.chat_messages.append({"role": "user", "content": question})
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": response.get("answer", "No answer"),
                        "sources": response.get("sources", [])
                    })
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {e}</div>', unsafe_allow_html=True)
        
        # Chat history
        if st.session_state.chat_messages:
            st.markdown("---")
            for msg in reversed(st.session_state.chat_messages[-10:]):  # Show last 10
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-msg">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-msg">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
                    if msg.get("sources"):
                        with st.expander(f"📚 Sources ({len(msg['sources'])} references)"):
                            for src in msg["sources"][:5]:
                                doc_name = src.get('document', 'Unknown')
                                page = src.get('page')
                                section = src.get('section')
                                similarity = src.get('similarity', 0)
                                preview = src.get('chunk_preview', '')
                                
                                # Build source display
                                source_line = f"📄 **{doc_name}**"
                                if page:
                                    source_line += f" • Page {page}"
                                if section:
                                    source_line += f" • {section}"
                                source_line += f" • {similarity*100:.1f}% match"
                                
                                st.markdown(source_line)
                                if preview:
                                    st.caption(f"_{preview}..._")
            
            if st.button("🗑️ Clear Chat", type="secondary"):
                st.session_state.chat_messages = []
                st.rerun()
        
        st.divider()
        
        # ===== SUGGESTED QUESTIONS SECTION =====
        st.markdown('<p class="section-header">💡 Suggested Questions - Explore Your Documents</p>', unsafe_allow_html=True)
        
        col_questions_btn, col_questions_num = st.columns([2, 1])
        with col_questions_btn:
            generate_btn = st.button("💡 Generate Questions", type="primary", use_container_width=True)
        with col_questions_num:
            num_q = st.selectbox("Questions", [3, 5, 8, 10], index=1, label_visibility="collapsed")
        
        if generate_btn:
            with st.spinner("Generating suggested questions..."):
                try:
                    result = generate_suggested_questions(num_q)
                    questions = result.get("questions", [])
                    st.session_state.suggested_questions = questions
                    if questions:
                        st.markdown(f'<div class="success-box">✅ Generated {len(questions)} suggested questions!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="info-box">No questions generated. Try uploading more content.</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {e}</div>', unsafe_allow_html=True)
        
        # Display suggested questions
        if st.session_state.suggested_questions:
            st.markdown("---")
            for idx, question in enumerate(st.session_state.suggested_questions):
                st.markdown(f'''
                <div class="quiz-question">
                    <p class="quiz-question-text">❓ Q{idx+1}: {question}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Button to ask this question directly in chat
                if st.button(f"💬 Ask This Question", key=f"ask_suggested_q_{idx}", use_container_width=True):
                    # Set the question in session state and trigger chat
                    st.session_state.last_question = question
                    st.rerun()
            
            # Clear quiz
            if st.button("🗑️ Clear Quiz", type="secondary"):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.rerun()
    
    # ===== FOOTER =====
    st.divider()
    col1, col2 = st.columns([4, 1])
    with col2:
        if num_docs > 0 and st.button("🗑️ Clear All Documents", type="secondary"):
            with st.spinner("Clearing documents..."):
                try:
                    clear_data()
                    st.session_state.chat_messages = []
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_answers = {}
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Clear failed: {e}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
        st.error(f"Error: {e}")
