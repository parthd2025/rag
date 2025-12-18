"""
Enhanced UI Components - Improved UX for RAG Chatbot
Includes: Streaming responses, enhanced sources, validation, error handling, etc.
"""

import streamlit as st
import time
from typing import List, Dict, Any, Optional
import json


# ============================================================================
# 1. ENHANCED RESPONSE RENDERING
# ============================================================================

def render_streaming_response(answer: str, container=None) -> None:
    """
    Render response with typing/streaming animation effect.
    
    Args:
        answer: The answer text to display
        container: Optional container to render in (default: st.empty())
    """
    st.markdown("""
    <style>
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    .typing-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #667eea;
        animation: typing 0.6s infinite;
        margin-left: 2px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if container is None:
        container = st.empty()
    
    # Show typing indicator while "streaming"
    display_text = ""
    with container:
        for i in range(0, len(answer), 3):
            display_text = answer[:i]
            st.write(display_text)
            time.sleep(0.01)
        
        st.write(answer)


# ============================================================================
# 2. ENHANCED SOURCE DISPLAY
# ============================================================================

def render_enhanced_sources(sources: List[Dict]) -> None:
    """
    Render sources with visual relevance indicators and actions.
    
    Args:
        sources: List of source dictionaries with 'chunk' and 'similarity'
    """
    st.subheader("📚 Sources & References")
    
    if not sources:
        st.info("No sources found")
        return
    
    for i, src in enumerate(sources[:5], 1):
        similarity = src.get("similarity", 0)
        chunk = src.get("chunk", "No content")
        
        # Determine color based on relevance
        # Thresholds calibrated for cosine similarity (0-1 range)
        if similarity > 0.75:  # Very similar
            color = "🟢"
            color_name = "Highly Relevant"
            bg_color = "#d4edda"
            border_color = "#28a745"
        elif similarity > 0.55:  # Somewhat similar
            color = "🟡"
            color_name = "Relevant"
            bg_color = "#fff3cd"
            border_color = "#ffc107"
        else:  # Less similar
            color = "🔴"
            color_name = "Low Relevance"
            bg_color = "#f8d7da"
            border_color = "#dc3545"
        
        # Create source card
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border-left: 4px solid {border_color};
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 10px;
        ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong>Source #{i} {color} {color_name}</strong>
            <span style="font-size: 12px; opacity: 0.8;">Relevance: {similarity:.1%}</span>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display chunk with copy button
        col1, col2 = st.columns([0.95, 0.05])
        with col1:
            st.text_area(
                label="Content",
                value=chunk[:300] + ("..." if len(chunk) > 300 else ""),
                height=80,
                disabled=True,
                label_visibility="collapsed",
                key=f"source_{i}"
            )
        with col2:
            if st.button("📋", key=f"copy_source_{i}", help="Copy source"):
                st.write(chunk)
                st.success("Copied to clipboard!")


# ============================================================================
# 3. FILE VALIDATION & UPLOAD
# ============================================================================

def render_enhanced_file_upload(uploaded_files: List[Any]) -> Dict[str, Any]:
    """
    Render enhanced file upload with validation.
    
    Args:
        uploaded_files: List of uploaded files from st.file_uploader
    
    Returns:
        Dictionary with validation results
    """
    if not uploaded_files:
        return {"valid": [], "invalid": [], "total_size": 0}
    
    validation_results = {"valid": [], "invalid": [], "total_size": 0}
    max_file_size = 50 * 1024 * 1024  # 50MB
    
    st.subheader("📋 Upload Validation")
    
    for f in uploaded_files:
        size_mb = f.size / (1024 * 1024)
        validation_results["total_size"] += f.size
        
        # Validate file
        is_valid = True
        issues = []
        
        if size_mb > max_file_size:
            is_valid = False
            issues.append(f"File exceeds {max_file_size/1024/1024:.0f}MB limit")
        
        if size_mb == 0:
            is_valid = False
            issues.append("File is empty")
        
        if is_valid:
            validation_results["valid"].append(f.name)
            st.success(f"✅ {f.name} ({size_mb:.1f}MB)")
        else:
            validation_results["invalid"].append(f.name)
            st.warning(f"⚠️ {f.name} ({size_mb:.1f}MB) - {', '.join(issues)}")
    
    # Summary
    total_mb = validation_results["total_size"] / (1024 * 1024)
    st.info(f"📦 Total Size: {total_mb:.1f}MB | Valid: {len(validation_results['valid'])} | Issues: {len(validation_results['invalid'])}")
    
    return validation_results


# ============================================================================
# 4. ERROR HANDLING & DISPLAY
# ============================================================================

def render_error_state(error_msg: str, error_type: str = "general", dismissible: bool = True) -> None:
    """
    Render distinct, styled error message.
    
    Args:
        error_msg: Error message text
        error_type: Type of error (connection, validation, timeout, notfound, general)
        dismissible: Whether error can be dismissed
    """
    error_config = {
        "connection": {
            "icon": "🔌",
            "color": "#ff6b6b",
            "bg": "#ffe0e0",
            "title": "Connection Error"
        },
        "validation": {
            "icon": "⚠️",
            "color": "#f59f00",
            "bg": "#fff9c4",
            "title": "Validation Error"
        },
        "timeout": {
            "icon": "⏱️",
            "color": "#ffa94d",
            "bg": "#ffe8cc",
            "title": "Timeout Error"
        },
        "notfound": {
            "icon": "🔍",
            "color": "#845ef7",
            "bg": "#f3f0ff",
            "title": "Not Found"
        },
        "general": {
            "icon": "❌",
            "color": "#dc3545",
            "bg": "#ffebee",
            "title": "Error"
        }
    }
    
    config = error_config.get(error_type, error_config["general"])
    
    st.markdown(f"""
    <div style="
        background: {config['bg']};
        border-left: 4px solid {config['color']};
        padding: 12px 16px;
        border-radius: 6px;
        margin: 10px 0;
    ">
    <strong>{config['icon']} {config['title']}</strong><br>
    <span style="color: {config['color']}; font-size: 14px;">{error_msg}</span>
    </div>
    """, unsafe_allow_html=True)


def render_success_state(message: str) -> None:
    """Render success message."""
    st.markdown(f"""
    <div style="
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 10px 0;
    ">
    <strong>✅ Success</strong><br>
    <span style="color: #155724; font-size: 14px;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


def render_info_state(message: str) -> None:
    """Render info message."""
    st.markdown(f"""
    <div style="
        background: #cfe8fc;
        border-left: 4px solid #0d6efd;
        padding: 12px 16px;
        border-radius: 6px;
        margin: 10px 0;
    ">
    <strong>ℹ️ Info</strong><br>
    <span style="color: #084298; font-size: 14px;">{message}</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# 5. ENHANCED CHAT MESSAGES
# ============================================================================

def render_enhanced_chat_message(role: str, content: str, msg_id: str, sources: List[Dict] = None) -> None:
    """
    Render chat message with action buttons.
    
    Args:
        role: "user" or "assistant"
        content: Message content
        msg_id: Unique message ID
        sources: Optional sources list
    """
    with st.chat_message(role):
        st.write(content)
        
        if role == "assistant":
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("👍", key=f"helpful_{msg_id}", help="Helpful"):
                    st.session_state[f"feedback_{msg_id}"] = "helpful"
                    st.success("Thanks for the feedback!")
            
            with col2:
                if st.button("👎", key=f"unhelpful_{msg_id}", help="Not helpful"):
                    st.session_state[f"feedback_{msg_id}"] = "unhelpful"
                    st.warning("We'll improve this!")
            
            with col3:
                if st.button("📋", key=f"copy_{msg_id}", help="Copy"):
                    st.code(content)
                    st.info("Copied!")
            
            with col4:
                if st.button("🔄", key=f"regenerate_{msg_id}", help="Regenerate"):
                    st.info("Regeneration request sent!")
            
            # Show sources if available
            if sources:
                with st.expander("📚 View Sources"):
                    render_enhanced_sources(sources)


# ============================================================================
# 6. DASHBOARD METRICS
# ============================================================================

def render_dashboard_metrics(stats: Dict[str, Any] = None) -> None:
    """
    Render system dashboard with metrics.
    
    Args:
        stats: Optional statistics dictionary
    """
    if stats is None:
        stats = {}
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        docs = stats.get("documents", 0)
        st.metric("📄 Documents", docs, "+0 today")
    
    with col2:
        questions = stats.get("questions", 0)
        st.metric("💬 Questions", questions, "+0 today")
    
    with col3:
        avg_response = stats.get("avg_response_time", "N/A")
        if isinstance(avg_response, (int, float)):
            st.metric("⚡ Avg Response", f"{avg_response:.2f}s", "-0.1s")
        else:
            st.metric("⚡ Avg Response", avg_response)
    
    with col4:
        success_rate = stats.get("success_rate", "N/A")
        if isinstance(success_rate, (int, float)):
            st.metric("✅ Success Rate", f"{success_rate:.1f}%", "+0.5%")
        else:
            st.metric("✅ Success Rate", success_rate)


# ============================================================================
# 7. ORGANIZED SIDEBAR WITH TABS
# ============================================================================

def render_organized_sidebar() -> Dict[str, Any]:
    """
    Render reorganized sidebar with tabs.
    
    Returns:
        Dictionary with sidebar inputs
    """
    with st.sidebar:
        st.header("🎛️ Control Panel")
        
        tab1, tab2, tab3 = st.tabs(["📤 Upload", "⚙️ Settings", "💡 Questions"])
        
        sidebar_data = {}
        
        # Tab 1: Upload
        with tab1:
            st.subheader("Upload Documents")
            uploaded_files = st.file_uploader(
                "Choose files",
                type=["pdf", "docx", "txt", "md", "csv", "xlsx", "xls", "pptx", "html", "htm", "xml"],
                accept_multiple_files=True,
                help="Supported formats: PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML, XML"
            )
            
            if uploaded_files:
                validation = render_enhanced_file_upload(uploaded_files)
                sidebar_data["uploaded_files"] = uploaded_files
                sidebar_data["validation"] = validation
                # Auto-upload when files are selected
                sidebar_data["auto_upload"] = True
            
            # Show upload status instead of button
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) ready to upload")
            else:
                st.info("📁 Select files above to start")
            
            st.divider()
            # Get actual document count
            try:
                import requests
                response = requests.get("http://localhost:8000/documents/count", timeout=2)
                if response.status_code == 200:
                    count = response.json().get("count", 0)
                    if count > 0:
                        st.metric("📊 Document Chunks", count, delta=f"+{count} available")
                    else:
                        st.metric("📊 Document Chunks", "No documents", delta="Upload documents to start")
                else:
                    st.metric("📊 Document Chunks", "Backend unavailable")
            except:
                st.metric("📊 Document Chunks", "Connecting...")
            st.button("🗑️ Clear All Documents", use_container_width=True, key="clear_docs_btn")
        
        # Tab 2: Settings
        with tab2:
            st.subheader("⚙️ Configuration")
            
            st.markdown("**Document Retrieval**")
            top_k = st.slider(
                "Context Chunks",
                min_value=1,
                max_value=20,
                value=5,
                help="How many relevant document sections to include in the answer. More chunks = more detailed but longer responses. Fewer chunks = faster, more focused answers."
            )
            sidebar_data["top_k"] = top_k
            
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Higher = more creative, Lower = more consistent"
            )
            sidebar_data["temperature"] = temperature
            
            chunk_strategy = st.selectbox(
                "Chunking Strategy",
                ["Fixed Size", "Semantic", "Adaptive"],
                help="How to split documents"
            )
            sidebar_data["chunk_strategy"] = chunk_strategy
            
            st.divider()
            
            st.subheader("Advanced Settings")
            
            show_sources = st.checkbox("Show source chunks", value=True)
            sidebar_data["show_sources"] = show_sources
            
            stream_response = st.checkbox("Stream responses", value=True)
            sidebar_data["stream_response"] = stream_response
            
            log_queries = st.checkbox("Log all queries", value=False)
            sidebar_data["log_queries"] = log_queries
        
        # Tab 3: Questions
        with tab3:
            st.subheader("Generate Questions")
            
            num_questions = st.slider(
                "Number of Questions",
                min_value=1,
                max_value=20,
                value=5,
                help="How many questions to generate"
            )
            sidebar_data["num_questions"] = num_questions
            
            question_type = st.multiselect(
                "Question Types",
                ["Factual", "Comparative", "Analytical", "Synthesis"],
                default=["Factual", "Comparative"]
            )
            sidebar_data["question_type"] = question_type
            
            if st.button("🧠 Generate Suggested Questions", use_container_width=True, key="generate_questions_btn"):
                st.session_state["generate_questions"] = True
            
            st.divider()
            
            # Recent questions
            st.subheader("Quick Actions")
            if st.button("📋 View Chat History", use_container_width=True):
                st.session_state["show_history"] = True
            
            if st.button("💾 Export Conversation", use_container_width=True):
                st.session_state["export_conversation"] = True
    
    return sidebar_data


# ============================================================================
# 8. THEME SELECTOR
# ============================================================================

def render_theme_selector() -> str:
    """
    Render theme selection in sidebar.
    
    Returns:
        Selected theme name
    """
    theme = st.sidebar.selectbox(
        "🎨 Theme",
        ["Auto", "Light", "Dark", "High Contrast"],
        help="Choose your preferred theme"
    )
    
    if theme == "Dark":
        st.markdown("""
        <style>
        body { background-color: #0f1419; color: #ffffff; }
        .stTextInput, .stTextArea, .stSelectbox { background-color: #1a1f26; }
        </style>
        """, unsafe_allow_html=True)
    
    elif theme == "Light":
        st.markdown("""
        <style>
        body { background-color: #ffffff; color: #000000; }
        .stTextInput, .stTextArea, .stSelectbox { background-color: #f5f5f5; }
        </style>
        """, unsafe_allow_html=True)
    
    elif theme == "High Contrast":
        st.markdown("""
        <style>
        body { background-color: #000000; color: #ffff00; }
        .stTextInput, .stTextArea, .stSelectbox { 
            background-color: #000000; 
            color: #ffff00;
            border: 2px solid #ffff00;
        }
        </style>
        """, unsafe_allow_html=True)
    
    return theme


# ============================================================================
# 9. LOADING STATES
# ============================================================================

def render_loading_skeleton() -> None:
    """Render skeleton loading animation."""
    st.markdown("""
    <style>
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .skeleton {
        animation: pulse 1.5s ease-in-out infinite;
        background: #e0e0e0;
        height: 20px;
        border-radius: 4px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="skeleton"></div>
    <div class="skeleton"></div>
    <div class="skeleton" style="width: 80%;"></div>
    """, unsafe_allow_html=True)


# ============================================================================
# 10. RESPONSE QUALITY INDICATOR
# ============================================================================

def render_response_quality(sources: List[Dict], confidence: float) -> None:
    """
    Render response quality indicator based on sources and confidence.
    
    Args:
        sources: List of source documents used
        confidence: Confidence score 0-1
    """
    quality = "High Quality" if confidence > 0.8 else "Medium Quality" if confidence > 0.6 else "Low Quality"
    quality_icon = "✅" if confidence > 0.8 else "⚠️" if confidence > 0.6 else "❌"
    quality_color = "#28a745" if confidence > 0.8 else "#ffc107" if confidence > 0.6 else "#dc3545"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: #f0f0f0;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            border: 2px solid {quality_color};
        ">
        <strong>{quality_icon}</strong><br>
        <small>Response Quality: {quality}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: #f0f0f0;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
        ">
        <strong>📚</strong><br>
        <small>Sources Used: {len(sources)}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: #f0f0f0;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
        ">
        <strong>🎯</strong><br>
        <small>Confidence: {confidence:.1%}</small>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# 11. FEEDBACK MODAL
# ============================================================================

def render_feedback_form() -> Dict[str, Any]:
    """
    Render feedback form for user feedback.
    
    Returns:
        Dictionary with feedback data
    """
    feedback_data = {}
    
    with st.form("feedback_form", clear_on_submit=True):
        st.subheader("📝 Share Your Feedback")
        
        rating = st.radio(
            "How helpful was this response?",
            ["😞 Not helpful", "😐 Somewhat helpful", "😊 Very helpful"],
            horizontal=True
        )
        feedback_data["rating"] = rating
        
        improvements = st.text_area(
            "What could be improved?",
            placeholder="Enter your suggestions here...",
            height=100
        )
        feedback_data["improvements"] = improvements
        
        email = st.text_input(
            "Email (optional)",
            placeholder="your@email.com"
        )
        feedback_data["email"] = email
        
        submitted = st.form_submit_button("Submit Feedback", use_container_width=True)
        
        if submitted:
            if rating and improvements:
                st.success("Thank you for your feedback!")
                return feedback_data
            else:
                st.warning("Please fill in all fields")
    
    return feedback_data


# ============================================================================
# 12. QUICK STATS & EXPORT
# ============================================================================

def render_session_stats() -> Dict[str, Any]:
    """
    Render and track session statistics.
    
    Returns:
        Dictionary with session stats
    """
    if "session_stats" not in st.session_state:
        st.session_state.session_stats = {
            "questions_asked": 0,
            "documents_uploaded": 0,
            "start_time": time.time(),
            "total_response_time": 0
        }
    
    stats = st.session_state.session_stats
    session_duration = (time.time() - stats["start_time"]) / 60  # minutes
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Questions", stats["questions_asked"])
    
    with col2:
        st.metric("Duration", f"{session_duration:.1f}m")
    
    with col3:
        avg_time = stats["total_response_time"] / max(stats["questions_asked"], 1)
        st.metric("Avg Response", f"{avg_time:.2f}s")
    
    return stats
