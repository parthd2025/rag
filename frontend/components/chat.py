"""
Chat Component - Enhanced with History, Confidence Scores, and Follow-up Suggestions
"""

import streamlit as st
import time
from typing import Dict, List, Any
from datetime import datetime


def render_chat_interface(api_client, config):
    """Enhanced chat interface with history, confidence scores, and suggestions."""
    
    # Initialize enhanced chat state
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = str(int(time.time()))
    
    # Chat header with conversation management
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.subheader("💬 Chat with Your Documents")
    
    with col2:
        # Conversation history length
        history_count = len([msg for msg in st.session_state.chat_messages if msg["role"] == "user"])
        if history_count > 0:
            st.metric("Questions", history_count)
    
    with col3:
        # Clear conversation button
        if st.button("🗑️ Clear Chat", help="Start a new conversation"):
            st.session_state.chat_messages = []
            st.session_state.conversation_history = []
            st.session_state.chat_id = str(int(time.time()))
            st.rerun()
    
    # Display conversation with enhanced formatting
    render_conversation_history()
    
    # Enhanced input section
    render_chat_input(api_client, config)
    
    # Follow-up suggestions
    render_follow_up_suggestions(api_client)


def render_conversation_history():
    """Render conversation with better formatting and confidence scores."""
    
    if not st.session_state.chat_messages:
        # Welcome message with tips
        st.markdown("""
        ### 🚀 Welcome to your Document Assistant!
        
        **💡 Tips for better results:**
        - Be specific in your questions
        - Ask about topics covered in your documents
        - Try comparative questions across documents
        - Use follow-up questions for deeper insights
        
        Upload documents and start asking questions about them!
        """)
        return
    
    # Render each message with enhanced formatting
    for i, msg in enumerate(st.session_state.chat_messages):
        if msg["role"] == "user":
            render_user_message(msg, i)
        else:
            render_assistant_message(msg, i)


def render_user_message(msg: Dict, index: int):
    """Render user message with timestamp."""
    with st.container():
        col1, col2 = st.columns([10, 2])
        
        with col1:
            st.markdown(f"""
            <div style="background-color: #2d2d2d; color: #ffffff; padding: 12px; border-radius: 10px; margin: 5px 0; border-right: 4px solid #0068c9;">
                <strong>🧑‍💼 You:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Show timestamp if available
            if msg.get('timestamp'):
                try:
                    dt = datetime.fromtimestamp(msg['timestamp'])
                    st.caption(dt.strftime("%H:%M"))
                except:
                    pass


def render_assistant_message(msg: Dict, index: int):
    """Render assistant message with confidence scores and sources."""
    with st.container():
        # Main response with better visibility
        st.markdown(f"""
        <div style="background-color: #1e1e1e; color: #ffffff; padding: 15px; border-radius: 10px; margin: 5px 0; border-left: 4px solid #00d4aa;">
            <strong>🤖 Assistant:</strong><br><br>
            <div style="line-height: 1.6; font-size: 14px;">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Response metadata
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            # Confidence score (if available)
            confidence = msg.get('confidence', 0.0)
            if confidence > 0:
                confidence_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                st.markdown(f"{confidence_color} Confidence: {confidence:.1%}")
        
        with col2:
            # Number of sources
            sources_count = len(msg.get("sources", []))
            if sources_count > 0:
                st.markdown(f"📚 {sources_count} sources")
        
        with col3:
            # Response time (if available)
            response_time = msg.get('response_time', 0)
            if response_time > 0:
                st.markdown(f"⏱️ {response_time:.1f}s")
        
        # Sources section with enhanced display
        if msg.get("sources"):
            render_sources_section(msg["sources"], index)


def render_sources_section(sources: List[Dict], msg_index: int):
    """Render sources with enhanced previews and confidence scores."""
    with st.expander(f"📖 View {len(sources)} Sources", expanded=False):
        for i, src in enumerate(sources, 1):
            # Source header with confidence
            doc_name = src.get('document_name', src.get('document', 'Unknown Document'))
            similarity = src.get('similarity', 0.0)
            
            # Confidence indicator
            confidence_emoji = "🎯" if similarity > 0.85 else "✅" if similarity > 0.7 else "⚠️"
            
            st.markdown(f"**{confidence_emoji} {doc_name}** • {similarity:.1%} relevance")
            
            # Enhanced preview
            preview = src.get('chunk_preview', src.get('formatted_preview', 'No preview available'))
            
            with st.expander(f"📄 Preview {i}", expanded=False):
                # Format preview with better readability
                if preview and preview.strip():
                    # Clean up preview text
                    cleaned_preview = preview.replace('\\n', '\n')
                    
                    # Limit preview length
                    if len(cleaned_preview) > 500:
                        cleaned_preview = cleaned_preview[:500] + "..."
                    
                    st.markdown(f"""
                    <div style="background-color: #2a2a2a; color: #ffffff; padding: 10px; border-left: 4px solid #00d4aa; font-family: monospace; border-radius: 5px;">
                        {cleaned_preview}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No preview available for this source")
                
                # Additional metadata
                if src.get('page_number'):
                    st.caption(f"📄 Page: {src['page_number']}")
                if src.get('chunk_index'):
                    st.caption(f"🧩 Chunk: {src['chunk_index']}")
            
            if i < len(sources):  # Don't add divider after last source
                st.divider()


def render_chat_input(api_client, config):
    """Enhanced chat input with better UX."""
    st.markdown("---")
    
    # Input section
    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_area(
            "Ask a question:",
            placeholder="What would you like to know about your documents?",
            height=80,
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")  # Spacing
        send_button = st.button(
            "🚀 Send", 
            use_container_width=True,
            type="primary"
        )
        
        # Quick actions
        if st.button("🎲 Surprise Me", use_container_width=True, help="Ask a random question"):
            # Generate a suggested question
            try:
                with st.spinner("Generating surprise question..."):
                    suggestions = api_client.generate_suggested_questions(5)
                    if suggestions and suggestions.get("questions"):
                        import random
                        question = random.choice(suggestions["questions"])
                        st.session_state["pending_question"] = question
                        st.rerun()
                    else:
                        st.error("No suggestions available. Upload some documents first!")
            except Exception as e:
                st.error(f"Failed to generate question: {str(e)}")
    
    # Handle pending question from Surprise Me
    if st.session_state.get("pending_question"):
        question = st.session_state["pending_question"]
        del st.session_state["pending_question"]
        # Auto-submit the surprise question
        process_question(api_client, config, question)
        return
    
    # Process question
    if send_button and question.strip():
        process_question(api_client, config, question.strip())


def process_question(api_client, config, question: str):
    """Process user question with enhanced error handling and metrics."""
    
    # Add user message with timestamp
    user_msg = {
        "role": "user", 
        "content": question,
        "timestamp": time.time()
    }
    st.session_state.chat_messages.append(user_msg)
    
    # Show processing indicator
    with st.spinner("🔍 Searching documents and generating response..."):
        try:
            start_time = time.time()
            
            # Get response from API
            response = api_client.query(question, top_k=config.get("TOP_K", 5))
            
            processing_time = time.time() - start_time
            
            # Calculate confidence based on source similarities
            sources = response.get("sources", [])
            avg_confidence = 0.0
            if sources:
                similarities = [src.get('similarity', 0.0) for src in sources]
                avg_confidence = sum(similarities) / len(similarities)
            
            # Add assistant response with metadata
            assistant_msg = {
                "role": "assistant",
                "content": response.get("answer", "I couldn't find relevant information in your documents."),
                "sources": sources,
                "confidence": avg_confidence,
                "response_time": processing_time,
                "timestamp": time.time()
            }
            
            st.session_state.chat_messages.append(assistant_msg)
            
            # Update conversation history for context
            st.session_state.conversation_history.append({
                "question": question,
                "answer": response.get("answer", ""),
                "confidence": avg_confidence
            })
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error processing question: {str(e)}")
            
            # Add error message to chat
            error_msg = {
                "role": "assistant",
                "content": f"Sorry, I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "timestamp": time.time()
            }
            st.session_state.chat_messages.append(error_msg)


def render_follow_up_suggestions(api_client):
    """Render follow-up question suggestions based on conversation."""
    
    if len(st.session_state.chat_messages) < 2:  # Need at least one Q&A pair
        return
    
    st.markdown("---")
    st.subheader("💡 Follow-up Suggestions")
    
    # Generate contextual suggestions
    suggestions = generate_contextual_suggestions()
    
    if suggestions:
        # Show 4 suggestions in a 2x2 grid
        col1, col2 = st.columns(2)
        
        for i, suggestion in enumerate(suggestions[:4]):
            with col1 if i % 2 == 0 else col2:
                if st.button(
                    suggestion,
                    key=f"suggestion_{i}",
                    use_container_width=True,
                    help="Click to ask this question"
                ):
                    process_question(api_client, config, suggestion)


def generate_contextual_suggestions() -> List[str]:
    """Generate contextual follow-up suggestions including doc-specific and cross-doc questions."""
    
    if not st.session_state.conversation_history:
        return []
    
    last_question = st.session_state.conversation_history[-1].get("question", "")
    
    # Document-specific suggestions
    doc_specific = [
        "What are the key findings in this specific document?",
        "Can you summarize the main points from this source?",
        "What methodology is used in this document?",
        "What are the limitations mentioned in this study?"
    ]
    
    # Cross-document comparison suggestions  
    cross_doc = [
        "How do these findings compare across different documents?",
        "What are the common themes between all documents?",
        "Which document provides the strongest evidence?",
        "Are there any contradictions between the sources?"
    ]
    
    # Context-based suggestions
    contextual = []
    
    if any(word in last_question.lower() for word in ["what", "define", "explain"]):
        contextual.extend([
            "Can you provide specific examples from the documents?",
            "What are the practical implications of this?"
        ])
    elif any(word in last_question.lower() for word in ["compare", "difference", "versus"]):
        contextual.extend([
            "Which approach is recommended?",
            "What are the trade-offs between these options?"
        ])
    elif any(word in last_question.lower() for word in ["how", "process", "method"]):
        contextual.extend([
            "Are there any best practices mentioned?",
            "What resources are needed for this?"
        ])
    
    # Combine suggestions (only if we have actual documents)
    all_suggestions = []
    if documents_info:
        all_suggestions = doc_specific[:2] + cross_doc[:2] + contextual[:2]
    
    # Return up to 4 suggestions
    return all_suggestions[:4] if all_suggestions else []
