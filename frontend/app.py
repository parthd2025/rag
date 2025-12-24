import streamlit as st
import requests
import logging

# Config
API_URL = "http://localhost:8001"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide", initial_sidebar_state="collapsed")

# Session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

# Dark theme CSS
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Hide sidebar */
    [data-testid="stSidebar"] { display: none; }
    
    /* Headers */
    h1, h2, h3, h4 { color: #ffffff !important; }
    p, span, label { color: #b0b0b0 !important; }
    
    /* Status cards */
    .status-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .status-label { color: #888 !important; font-size: 12px; text-transform: uppercase; }
    .status-value { color: #fff !important; font-size: 28px; font-weight: 600; }
    .status-online { color: #00ff88 !important; }
    
    /* Upload area */
    .upload-zone {
        background: rgba(255,255,255,0.03);
        border: 2px dashed rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 30px;
        text-align: center;
        margin: 10px 0;
    }
    .upload-zone:hover { border-color: #4da6ff; background: rgba(77,166,255,0.05); }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0078D4 0%, #00a8ff 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,120,212,0.4);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.03);
        border: 2px dashed rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 20px;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #4da6ff;
    }
    
    /* Text input */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px;
        color: #fff !important;
        padding: 12px 16px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4da6ff !important;
        box-shadow: 0 0 0 2px rgba(77,166,255,0.2);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] { color: #fff !important; font-size: 24px !important; }
    [data-testid="stMetricLabel"] { color: #888 !important; }
    
    /* Messages */
    .user-msg {
        background: linear-gradient(135deg, #0078D4 0%, #00a8ff 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 12px 12px 4px 12px;
        margin: 8px 0;
    }
    .bot-msg {
        background: rgba(255,255,255,0.08);
        color: #e0e0e0;
        padding: 12px 16px;
        border-radius: 12px 12px 12px 4px;
        margin: 8px 0;
    }
    
    /* Info/Warning/Error boxes */
    .info-box {
        background: rgba(77,166,255,0.1);
        border-left: 4px solid #4da6ff;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        color: #a0d4ff !important;
    }
    .success-box {
        background: rgba(0,255,136,0.1);
        border-left: 4px solid #00ff88;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        color: #00ff88 !important;
    }
    .error-box {
        background: rgba(255,77,77,0.1);
        border-left: 4px solid #ff4d4d;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        color: #ff6b6b !important;
    }
    
    /* Divider */
    hr { border-color: rgba(255,255,255,0.1) !important; margin: 20px 0 !important; }
    
    /* File list */
    .file-item {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px 0;
        display: flex;
        align-items: center;
    }
    
    /* Section headers */
    .section-header {
        color: #ffa726 !important;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    /* Source reference styles */
    .source-ref {
        background: rgba(77,166,255,0.1);
        border-left: 3px solid #4da6ff;
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 0 6px 6px 0;
    }
    .source-doc { color: #4da6ff !important; font-weight: 500; }
    .source-page { color: #ffa726 !important; }
    .source-similarity { color: #00ff88 !important; }
    .source-preview { color: #888 !important; font-style: italic; font-size: 12px; }
    
    /* Quiz styles */
    .quiz-question {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }
    .quiz-question-text {
        color: #fff !important;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 15px;
    }
    .quiz-btn {
        background: rgba(77,166,255,0.2);
        border: 1px solid rgba(77,166,255,0.4);
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px 0;
        color: #a0d4ff !important;
        cursor: pointer;
        transition: all 0.2s;
    }
    .quiz-btn:hover {
        background: rgba(77,166,255,0.3);
        border-color: #4da6ff;
    }
</style>
""", unsafe_allow_html=True)


def check_api():
    """Check backend connection."""
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        return r.status_code == 200
    except:
        return False


def get_stats():
    """Get document stats."""
    try:
        r = requests.get(f"{API_URL}/documents", timeout=5)
        if r.status_code == 200:
            data = r.json()
            # Backend returns 'chunks' and 'documents' list
            docs = data.get("documents", [])
            chunks = data.get("chunks", 0)
            return docs, chunks  # Return full docs list
    except:
        pass
    return [], 0


def get_documents():
    """Get list of documents with their chunk counts."""
    try:
        r = requests.get(f"{API_URL}/documents", timeout=5)
        if r.status_code == 200:
            return r.json().get("documents", [])
    except:
        pass
    return []


def delete_document(doc_name):
    """Delete a specific document."""
    try:
        r = requests.delete(f"{API_URL}/documents/{doc_name}", timeout=30)
        r.raise_for_status()
        return True
    except:
        return False


def upload_files(files_list):
    """Upload multiple files to backend."""
    import mimetypes
    try:
        # Backend expects 'files' as List[UploadFile]
        # Format: [("files", (filename, data, content_type)), ...]
        files_data = []
        for f in files_list:
            content_type = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            files_data.append(("files", (f.name, f.getvalue(), content_type)))
        
        r = requests.post(f"{API_URL}/upload", files=files_data, timeout=120)
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


def ask_question(question, top_k=5):
    """Send question to backend."""
    try:
        r = requests.post(f"{API_URL}/chat", json={"question": question, "top_k": top_k}, timeout=60)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        raise Exception(f"{e}")


def clear_data():
    """Clear all documents."""
    try:
        # Backend uses DELETE method for /clear
        r = requests.delete(f"{API_URL}/clear", timeout=30)
        r.raise_for_status()
        return True
    except:
        return False


def generate_quiz(num_questions=5):
    """Generate quiz questions from documents."""
    try:
        r = requests.post(f"{API_URL}/quiz", json={"num_questions": num_questions}, timeout=120)
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
        response = requests.get(f"{API_URL}/settings", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("settings", data)
    except Exception:
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
    docs_list, chunks = get_stats() if connected else ([], 0)
    num_docs = len(docs_list) if isinstance(docs_list, list) else 0
    
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
        default_single = int(settings_data.get("max_questions_single", 10) or 10)
        default_multi = int(settings_data.get("max_questions_multi", 20) or 20)

        with st.form("settings_form"):
            col_left, col_right = st.columns(2)
            with col_left:
                chunking_level = st.slider("Chunking Level", 1, 10, default_chunking)
                context_window = st.slider("Context Window (characters)", 256, 8192, default_context, step=128)
            with col_right:
                top_k = st.slider("Retrieval Top K", 1, 20, default_top_k)
                temperature = st.slider("LLM Temperature", 0.0, 2.0, default_temperature, 0.05)

            col_single, col_multi = st.columns(2)
            with col_single:
                max_single = st.number_input("Suggested Questions (Single Doc)", min_value=1, max_value=50, value=default_single)
            with col_multi:
                max_multi = st.number_input("Suggested Questions (Multi Doc)", min_value=1, max_value=50, value=default_multi)

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
            if max_single != default_single:
                payload["max_questions_single"] = int(max_single)
            if max_multi != default_multi:
                payload["max_questions_multi"] = int(max_multi)

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
    
    # ===== DOCUMENT LIST =====
    if docs_list:
        st.markdown('<p class="section-header">📚 Documents</p>', unsafe_allow_html=True)
        for doc in docs_list:
            col_name, col_chunks, col_del = st.columns([4, 1, 1])
            with col_name:
                st.markdown(f'📄 {doc.get("name", "Unknown")}')
            with col_chunks:
                st.caption(f'{doc.get("chunks", 0)} chunks')
            with col_del:
                if st.button("🗑️", key=f"del_{doc.get('name')}", help=f"Delete {doc.get('name')}"):
                    if delete_document(doc.get("name")):
                        st.rerun()
    
    st.divider()
    
    # ===== CHAT SECTION =====
    if chunks == 0:
        st.markdown('<div class="info-box">👆 Upload documents above to start</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="section-header">💬 Ask a Question</p>', unsafe_allow_html=True)
        
        col_input, col_btn = st.columns([6, 1])
        
        with col_input:
            question = st.text_input("Question", placeholder="What would you like to know?", label_visibility="collapsed")
        
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
        
        # ===== QUIZ SECTION =====
        st.markdown('<p class="section-header">📝 Quiz - Test Your Knowledge</p>', unsafe_allow_html=True)
        
        col_quiz_btn, col_quiz_num = st.columns([2, 1])
        with col_quiz_btn:
            generate_btn = st.button("🎯 Generate Questions", type="primary", use_container_width=True)
        with col_quiz_num:
            num_q = st.selectbox("Questions", [3, 5, 7, 10], index=1, label_visibility="collapsed")
        
        if generate_btn:
            with st.spinner("Generating questions from your documents..."):
                try:
                    result = generate_quiz(num_q)
                    questions = result.get("questions", [])
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_answers = {}
                    if questions:
                        st.markdown(f'<div class="success-box">✅ Generated {len(questions)} questions!</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="info-box">No questions generated. Try uploading more content.</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {e}</div>', unsafe_allow_html=True)
        
        # Display quiz questions
        if st.session_state.quiz_questions:
            st.markdown("---")
            for idx, q in enumerate(st.session_state.quiz_questions):
                q_text = q.get("question", q) if isinstance(q, dict) else q
                q_type = q.get("type", "general") if isinstance(q, dict) else "general"
                
                st.markdown(f'''
                <div class="quiz-question">
                    <p class="quiz-question-text">❓ Q{idx+1}: {q_text}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Button to ask this question
                col_ask, col_type = st.columns([3, 1])
                with col_ask:
                    if st.button(f"💡 Get Answer", key=f"ask_q_{idx}", use_container_width=True):
                        with st.spinner("Getting answer..."):
                            try:
                                answer = ask_question(q_text)
                                st.session_state.quiz_answers[idx] = answer
                            except Exception as e:
                                st.error(f"Error: {e}")
                with col_type:
                    st.caption(f"📌 {q_type}")
                
                # Show answer if available
                if idx in st.session_state.quiz_answers:
                    ans = st.session_state.quiz_answers[idx]
                    st.markdown(f'<div class="bot-msg">💡 {ans.get("answer", "No answer")}</div>', unsafe_allow_html=True)
                    if ans.get("sources"):
                        with st.expander(f"📚 Sources ({len(ans['sources'])} references)"):
                            for src in ans["sources"][:5]:
                                doc_name = src.get('document', 'Unknown')
                                page = src.get('page')
                                section = src.get('section')
                                similarity = src.get('similarity', 0)
                                preview = src.get('chunk_preview', '')
                                
                                source_line = f"📄 **{doc_name}**"
                                if page:
                                    source_line += f" • Page {page}"
                                if section:
                                    source_line += f" • {section}"
                                source_line += f" • {similarity*100:.1f}% match"
                                
                                st.markdown(source_line)
                                if preview:
                                    st.caption(f"_{preview}..._")
            
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
            if clear_data():
                st.session_state.chat_messages = []
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.rerun()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
        st.error(f"Error: {e}")
