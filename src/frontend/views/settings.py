"""
Settings Page - System configuration
"""

import streamlit as st
from typing import Dict, Any
import time

from components.state import get_state, set_state, get_api_client


def render_settings_page():
    """Render the settings configuration page."""
    
    api = get_api_client()
    if not api:
        st.error("API client not available. Please check connection.")
        return
    
    try:
        config = api.get_config()
        if not config:
            st.error("❌ Could not load configuration from backend")
            return
        
        # Settings tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔍 Search & Retrieval",
            "🤖 Language Model",
            "📊 Processing",
            "🎯 Advanced"
        ])
        
        with tab1:
            _render_search_settings(api, config)
        
        with tab2:
            _render_llm_settings(api, config)
        
        with tab3:
            _render_processing_settings(api, config)
        
        with tab4:
            _render_advanced_settings(api, config)
            
    except Exception as e:
        st.error(f"❌ Error loading settings: {str(e)}")


def _render_search_settings(api, config: Dict[str, Any]):
    """Render search and retrieval settings."""
    
    st.markdown("### 🔍 Search & Retrieval Configuration")
    st.caption("Configure how documents are searched and results are retrieved.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top-K results
        current_top_k = config.get("TOP_K", 5)
        new_top_k = st.slider(
            "Top-K Results",
            min_value=1,
            max_value=20,
            value=current_top_k,
            step=1,
            help="Number of most relevant chunks to retrieve"
        )
        
        # Similarity threshold
        current_threshold = config.get("SIMILARITY_THRESHOLD", 0.3)
        new_threshold = st.slider(
            "Similarity Threshold",
            min_value=0.0,
            max_value=1.0,
            value=current_threshold,
            step=0.05,
            format="%.2f",
            help="Minimum similarity score for results"
        )
        
        # Context window
        current_context = config.get("CONTEXT_WINDOW_SIZE", 2500)
        new_context = st.number_input(
            "Context Window Size",
            min_value=1000,
            max_value=10000,
            value=current_context,
            step=500,
            help="Maximum characters in LLM context"
        )
    
    with col2:
        st.markdown("**📊 Impact Preview**")
        
        # Show impact of changes
        if new_top_k != current_top_k:
            impact = "🔼 More sources" if new_top_k > current_top_k else "🔽 Fewer sources"
            st.info(f"Top-K: {impact}")
        
        if abs(new_threshold - current_threshold) > 0.05:
            if new_threshold > current_threshold:
                st.info("🎯 Higher quality, fewer results")
            else:
                st.info("🌐 Lower threshold, more results")
        
        if abs(new_context - current_context) > 500:
            if new_context > current_context:
                st.info("📚 More context, slower responses")
            else:
                st.info("⚡ Less context, faster responses")
        
        # Current values card
        st.markdown("**Current Values:**")
        st.write(f"• Top-K: {current_top_k}")
        st.write(f"• Threshold: {current_threshold:.2f}")
        st.write(f"• Context: {current_context:,} chars")
    
    # Apply button
    search_settings = {
        "TOP_K": new_top_k,
        "SIMILARITY_THRESHOLD": new_threshold,
        "CONTEXT_WINDOW_SIZE": new_context
    }
    
    if st.button("🔍 Apply Search Settings", use_container_width=True, type="primary"):
        _apply_settings(api, search_settings, "Search")


def _render_llm_settings(api, config: Dict[str, Any]):
    """Render LLM settings."""
    
    st.markdown("### 🤖 Language Model Configuration")
    st.caption("Configure how the AI generates responses.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature
        current_temp = config.get("TEMPERATURE", 0.3)
        new_temp = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=current_temp,
            step=0.1,
            format="%.1f",
            help="Response creativity (0=focused, 2=creative)"
        )
        
        # Max tokens
        current_max_tokens = config.get("MAX_TOKENS", 800)
        new_max_tokens = st.slider(
            "Max Response Tokens",
            min_value=100,
            max_value=2000,
            value=current_max_tokens,
            step=50,
            help="Maximum response length"
        )
        
        # Model info (read-only)
        current_model = config.get("MODEL_NAME", "llama-3.3-70b-versatile")
        st.text_input(
            "Model Name",
            value=current_model,
            disabled=True,
            help="Change in backend configuration"
        )
    
    with col2:
        st.markdown("**🎨 Response Style**")
        
        # Temperature description
        temp_desc = _get_temperature_description(new_temp)
        st.info(f"🌡️ {temp_desc}")
        
        # Length description
        length_desc = _get_length_description(new_max_tokens)
        st.info(f"📏 {length_desc}")
        
        st.markdown("**Response Options:**")
        
        use_citations = st.checkbox(
            "Include Source Citations",
            value=True,
            help="Add document references to responses"
        )
        
        use_confidence = st.checkbox(
            "Show Confidence Scores",
            value=True,
            help="Display confidence indicators"
        )
    
    # Apply button
    llm_settings = {
        "TEMPERATURE": new_temp,
        "MAX_TOKENS": new_max_tokens
    }
    
    if st.button("🤖 Apply LLM Settings", use_container_width=True, type="primary"):
        _apply_settings(api, llm_settings, "LLM")


def _render_processing_settings(api, config: Dict[str, Any]):
    """Render document processing settings."""
    
    st.markdown("### 📊 Document Processing Configuration")
    st.caption("Configure how documents are chunked and processed.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Max file size
        current_max_size = get_state("max_file_size_mb", 100)
        new_max_size = st.slider(
            "📁 Max File Size (MB)",
            min_value=1,
            max_value=100,
            value=current_max_size,
            step=5,
            help="Maximum allowed file size for uploads"
        )
        set_state("max_file_size_mb", new_max_size)
        
        st.divider()
        
        # Chunk size
        current_chunk_size = config.get("CHUNK_SIZE", 1000)
        new_chunk_size = st.slider(
            "Chunk Size",
            min_value=200,
            max_value=2000,
            value=current_chunk_size,
            step=100,
            help="Characters per document chunk"
        )
        
        # Chunk overlap
        current_overlap = config.get("CHUNK_OVERLAP", 200)
        max_overlap = min(500, new_chunk_size // 2)
        new_overlap = st.slider(
            "Chunk Overlap",
            min_value=0,
            max_value=max_overlap,
            value=min(current_overlap, max_overlap),
            step=50,
            help="Character overlap between chunks"
        )
        
        # Embedding model (read-only)
        embedding_model = config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        st.text_input(
            "Embedding Model",
            value=embedding_model,
            disabled=True,
            help="Requires restart to change"
        )
    
    with col2:
        st.markdown("**📊 Processing Impact**")
        
        # Overlap percentage
        overlap_pct = (new_overlap / new_chunk_size) * 100 if new_chunk_size > 0 else 0
        st.metric("Overlap Percentage", f"{overlap_pct:.1f}%")
        
        # Estimated chunks per doc
        avg_doc_size = 50000  # chars
        est_chunks = max(1, (avg_doc_size - new_overlap) // (new_chunk_size - new_overlap)) if new_chunk_size > new_overlap else 1
        st.metric("Est. Chunks/Doc", int(est_chunks))
        
        # Recommendations
        if new_chunk_size < 500:
            st.warning("⚠️ Small chunks may lose context")
        elif new_chunk_size > 1500:
            st.info("📚 Large chunks preserve more context")
        
        if overlap_pct > 50:
            st.warning("⚠️ High overlap increases storage")
        elif overlap_pct < 10:
            st.warning("⚠️ Low overlap may lose connections")
    
    st.info("📝 Processing settings apply to **newly uploaded** documents only.")
    
    # Apply button
    processing_settings = {
        "CHUNK_SIZE": new_chunk_size,
        "CHUNK_OVERLAP": new_overlap
    }
    
    if st.button("📊 Apply Processing Settings", use_container_width=True, type="primary"):
        _apply_settings(api, processing_settings, "Processing")


def _render_advanced_settings(api, config: Dict[str, Any]):
    """Render advanced settings and diagnostics."""
    
    st.markdown("### 🎯 Advanced Configuration & Diagnostics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 System Information**")
        
        try:
            doc_stats = api.get_documents()
            if doc_stats:
                st.metric("Total Documents", len(doc_stats.get("documents", [])))
                st.metric("Total Chunks", doc_stats.get("chunks", doc_stats.get("total_chunks", 0)))
            
            # API test
            if st.button("🔄 Test API Response"):
                start = time.time()
                health = api.health_check()
                response_time = time.time() - start
                
                if health:
                    st.success(f"✅ API responding in {response_time:.3f}s")
                else:
                    st.error("❌ API health check failed")
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with col2:
        st.markdown("**🔧 Maintenance**")
        
        if st.button("🔄 Re-index Documents", use_container_width=True):
            st.warning("⚠️ Requires backend implementation")
        
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.info("💡 Cache cleared (if implemented)")
        
        # Export config
        if st.button("📥 Export Settings", use_container_width=True):
            import json
            config_json = json.dumps(config, indent=2)
            st.download_button(
                "💾 Download Config",
                data=config_json,
                file_name="rag_config.json",
                mime="application/json"
            )
    
    # Danger zone
    st.divider()
    st.markdown("### ⚠️ Danger Zone")
    
    col1, col2 = st.columns(2)
    
    with col1:
        confirm_reset = st.checkbox("I want to reset all settings")
        
        if st.button("🔄 Reset to Defaults", disabled=not confirm_reset, use_container_width=True):
            default_settings = _get_default_settings()
            _apply_settings(api, default_settings, "Reset")
    
    with col2:
        # Raw config view
        with st.expander("🔍 View Raw Configuration"):
            st.json(config)


def _get_temperature_description(temp: float) -> str:
    """Get description for temperature setting."""
    if temp < 0.3:
        return "Very focused and deterministic"
    elif temp < 0.7:
        return "Balanced creativity and consistency"
    elif temp < 1.2:
        return "Creative with some variability"
    else:
        return "Highly creative and diverse"


def _get_length_description(tokens: int) -> str:
    """Get description for max tokens setting."""
    if tokens < 300:
        return "Short, concise responses"
    elif tokens < 800:
        return "Moderate length responses"
    elif tokens < 1200:
        return "Detailed responses"
    else:
        return "Very detailed, comprehensive"


def _get_default_settings() -> Dict[str, Any]:
    """Get default configuration settings."""
    return {
        "TOP_K": 5,
        "SIMILARITY_THRESHOLD": 0.3,
        "CONTEXT_WINDOW_SIZE": 2500,
        "TEMPERATURE": 0.3,
        "MAX_TOKENS": 800,
        "CHUNK_SIZE": 1000,
        "CHUNK_OVERLAP": 200
    }


def _apply_settings(api, settings: Dict[str, Any], category: str):
    """Apply settings update."""
    try:
        # Attempt to update via API
        result = api.update_settings(settings)
        
        if result:
            st.success(f"✅ {category} settings updated successfully!")
            time.sleep(1)
            st.rerun()
        else:
            # Fallback: show what would be updated
            st.success(f"✅ {category} settings would be updated:")
            for key, value in settings.items():
                st.write(f"• {key}: {value}")
            st.info("💡 Settings update endpoint may need backend implementation")
            
    except Exception as e:
        st.error(f"❌ Error updating {category} settings: {str(e)}")
