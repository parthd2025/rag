"""
Upload Page - Document upload and processing
"""

import streamlit as st
import time
from typing import List, Any

from components.state import get_state, set_state, get_api_client


def render_upload_page():
    """Render the document upload page."""
    
    api = get_api_client()
    if not api:
        st.error("API client not available. Please check connection.")
        return
    
    # Upload section
    _render_upload_section(api)
    
    st.divider()
    
    # Upload tips
    _render_upload_tips()


def _render_upload_section(api):
    """Render the main upload section."""
    
    st.markdown("### 📤 Upload Documents")
    
    # Get max file size from session state
    max_file_size_mb = get_state("max_file_size_mb", 100)
    max_file_size_bytes = max_file_size_mb * 1024 * 1024
    
    st.caption(f"📁 Max file size: {max_file_size_mb} MB (configurable in Settings)")
    
    # File uploader
    files = st.file_uploader(
        "Select documents to upload:",
        type=["pdf", "docx", "txt", "md", "csv", "xlsx", "pptx", "html"],
        accept_multiple_files=True,
        help=f"Supported: PDF, Word, Text, Markdown, CSV, Excel, PowerPoint, HTML. Max: {max_file_size_mb} MB"
    )
    
    if not files:
        # Empty state
        st.markdown("""
        <div style="border: 2px dashed #404040; border-radius: 12px; padding: 3rem; 
                    text-align: center; margin: 1rem 0;">
            <p style="font-size: 1.2rem; margin: 0;">
                📁 Drag and drop files here or click to browse
            </p>
            <p style="color: #888; margin: 0.5rem 0 0 0;">
                Supports PDF, Word, Text, Markdown, CSV, Excel, PowerPoint, HTML
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Filter files by size
    valid_files = []
    oversized_files = []
    
    for f in files:
        if f.size <= max_file_size_bytes:
            valid_files.append(f)
        else:
            oversized_files.append(f)
    
    # Show warning for oversized files
    if oversized_files:
        st.warning(f"⚠️ {len(oversized_files)} file(s) exceed the {max_file_size_mb} MB limit:")
        for f in oversized_files:
            size_mb = f.size / (1024 * 1024)
            st.write(f"  • {f.name} ({size_mb:.1f} MB)")
    
    if not valid_files:
        st.error("❌ No files within size limit to upload")
        return
    
    # File preview
    st.markdown(f"**📋 {len(valid_files)} file(s) ready for upload:**")
    
    _render_file_preview(valid_files)
    
    # Upload controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        upload_button = st.button(
            f"🚀 Upload {len(valid_files)} File(s)",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        batch_size = st.selectbox(
            "Batch size:",
            [1, 3, 5, 10],
            index=1,
            help="Files to process simultaneously"
        )
    
    with col3:
        show_details = st.checkbox("Show details", value=True)
    
    if upload_button:
        _upload_with_progress(api, valid_files, batch_size, show_details)


def _render_file_preview(files: List[Any]):
    """Render file preview table."""
    
    # Header
    header_cols = st.columns([4, 2, 2, 2])
    with header_cols[0]:
        st.markdown("**File Name**")
    with header_cols[1]:
        st.markdown("**Size**")
    with header_cols[2]:
        st.markdown("**Type**")
    with header_cols[3]:
        st.markdown("**Status**")
    
    # File rows
    for f in files:
        row_cols = st.columns([4, 2, 2, 2])
        
        with row_cols[0]:
            icon = _get_file_icon(f.name)
            st.write(f"{icon} {f.name}")
        
        with row_cols[1]:
            size_mb = f.size / (1024 * 1024)
            if size_mb < 1:
                st.write(f"{f.size / 1024:.1f} KB")
            else:
                st.write(f"{size_mb:.1f} MB")
        
        with row_cols[2]:
            ext = f.name.split('.')[-1].upper() if '.' in f.name else 'FILE'
            st.write(ext)
        
        with row_cols[3]:
            st.write("⏳ Ready")


def _upload_with_progress(api, files: List[Any], batch_size: int, show_details: bool):
    """Handle batch upload with progress tracking."""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    success_count = 0
    total_chunks = 0
    failed_files = []
    
    # Process files in batches
    for batch_start in range(0, len(files), batch_size):
        batch = files[batch_start:batch_start + batch_size]
        
        for i, f in enumerate(batch):
            current_file = batch_start + i + 1
            progress = current_file / len(files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {current_file}/{len(files)}: {f.name}")
            
            try:
                start_time = time.time()
                result = api.upload_document(f.getvalue(), f.name)
                processing_time = time.time() - start_time
                
                chunks = result.get('chunks_created', 0)
                total_chunks += chunks
                success_count += 1
                
                if show_details:
                    with results_container:
                        cols = st.columns([4, 2, 2, 2])
                        with cols[0]:
                            st.write(f"✅ {f.name}")
                        with cols[1]:
                            st.write(f"{chunks} chunks")
                        with cols[2]:
                            st.write(f"{processing_time:.1f}s")
                        with cols[3]:
                            st.write("Success")
                            
            except Exception as e:
                failed_files.append((f.name, str(e)))
                if show_details:
                    with results_container:
                        st.write(f"❌ {f.name}: {str(e)}")
    
    # Final results
    progress_bar.progress(1.0)
    status_text.empty()
    
    # Summary
    if success_count > 0:
        st.success(
            f"🎉 **Upload Complete!**\n\n"
            f"✅ {success_count}/{len(files)} files processed\n\n"
            f"📊 Total chunks created: {total_chunks:,}"
        )
    
    if failed_files:
        st.error(f"❌ {len(failed_files)} files failed:")
        for name, error in failed_files:
            st.write(f"• {name}: {error}")
    
    # Auto-refresh
    time.sleep(1)
    st.rerun()


def _render_upload_tips():
    """Render upload tips section."""
    
    st.markdown("### 💡 Upload Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📚 Supported File Types:**
        
        | Format | Extensions |
        |--------|------------|
        | Documents | PDF, DOCX, TXT, MD |
        | Spreadsheets | CSV, XLSX |
        | Presentations | PPTX |
        | Web | HTML |
        """)
    
    with col2:
        st.markdown("""
        **🎯 Best Practices:**
        
        - **Text-readable**: Ensure PDFs are not scanned images
        - **Organized**: Group related documents together
        - **Size**: Larger documents = more processing time
        - **Quality**: Clean, well-formatted documents work best
        """)
    
    with st.expander("📖 Understanding Chunking", expanded=False):
        st.markdown("""
        Documents are split into smaller "chunks" for efficient searching:
        
        - **Chunk Size**: ~1000 characters per chunk
        - **Overlap**: Some overlap between chunks ensures context is preserved
        - **Search**: When you ask a question, relevant chunks are retrieved
        
        More chunks = more granular search, but may fragment context.
        Fewer chunks = broader context, but may miss specific details.
        
        Configure chunk settings in the **Settings** page.
        """)


def _get_file_icon(filename: str) -> str:
    """Get emoji icon based on file extension."""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    icons = {
        'pdf': '📄', 'docx': '📝', 'doc': '📝', 'txt': '📄', 'md': '📑',
        'csv': '📊', 'xlsx': '📈', 'xls': '📈', 'pptx': '📺', 'ppt': '📺',
        'html': '🌐', 'htm': '🌐'
    }
    return icons.get(ext, '📄')
