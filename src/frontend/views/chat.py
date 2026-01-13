"""
Chat Page - Main chatbot interface
"""

import streamlit as st
import time
from typing import Dict, List, Any
from datetime import datetime

from components.state import (
    get_state, set_state, get_api_client,
    clear_chat_state
)


def render_chat_page():
    """Render the main chat interface page."""
    
    api = get_api_client()
    if not api:
        st.error("API client not available. Please check connection.")
        return
    
    total_chunks = get_state("total_chunks", 0)
    total_docs = get_state("total_docs", 0)
    
    # Page-specific header with comparison toggle
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        if total_chunks == 0:
            st.info("📝 **No documents yet.** Upload documents in the 'Upload' page to start asking questions!")
        else:
            st.success(f"📚 **{total_chunks:,} chunks ready** from {total_docs} document(s). Ask me anything!")
    
    with col2:
        # Model comparison toggle
        comparison_mode = st.checkbox(
            "🔬 Compare Models",
            value=get_state("comparison_mode", False),
            help="Enable to compare responses from different models with quality scores"
        )
        set_state("comparison_mode", comparison_mode)
    
    with col3:
        # Clear conversation button
        if st.button("🗑️ Clear Chat", help="Start a new conversation", use_container_width=True):
            clear_chat_state()
            st.rerun()
    
    # Display conversation history
    _render_conversation_history()
    
    # Chat input
    _render_chat_input(api)
    
    # Follow-up suggestions
    _render_follow_up_suggestions(api)


def _render_conversation_history():
    """Render the conversation history with enhanced formatting."""
    
    chat_messages = get_state("chat_messages", [])
    
    if not chat_messages:
        # Welcome message
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); 
                    padding: 2rem; border-radius: 12px; margin: 1rem 0;">
            <h3 style="margin: 0 0 1rem 0; color: #fff;">🚀 Welcome to your Document Assistant!</h3>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0;">
                <strong>💡 Tips for better results:</strong>
            </p>
            <ul style="color: rgba(255,255,255,0.85); margin: 0.5rem 0;">
                <li>Be specific in your questions</li>
                <li>Ask about topics covered in your documents</li>
                <li>Try comparative questions across documents</li>
                <li>Use follow-up questions for deeper insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Render each message
    for i, msg in enumerate(chat_messages):
        if msg["role"] == "user":
            _render_user_message(msg, i)
        else:
            _render_assistant_message(msg, i)


def _render_user_message(msg: Dict, index: int):
    """Render a user message."""
    
    with st.container():
        st.markdown(f"""
        <div style="background-color: #2d2d2d; color: #ffffff; padding: 12px 16px; 
                    border-radius: 12px; margin: 8px 0; border-right: 4px solid #0068c9;">
            <strong>🧑‍💼 You:</strong> {msg['content']}
        </div>
        """, unsafe_allow_html=True)


def _render_assistant_message(msg: Dict, index: int):
    """Render an assistant message with sources and metadata."""
    
    is_comparison = msg.get("is_comparison", False)
    
    with st.container():
        # Main response
        st.markdown(f"""
        <div style="background-color: #1e1e1e; color: #ffffff; padding: 16px; 
                    border-radius: 12px; margin: 8px 0; border-left: 4px solid #00d4aa;">
            <strong>🤖 Assistant:</strong>
            <div style="line-height: 1.7; font-size: 14px; margin-top: 8px;">
                {msg['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Comparison mode: Show model comparison details
        if is_comparison and msg.get("comparison_data"):
            _render_comparison_details(msg["comparison_data"])
        
        # Response metadata row
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            confidence = msg.get('confidence', 0.0)
            if confidence > 0:
                emoji = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                label = "Quality Score" if is_comparison else "Confidence"
                st.caption(f"{emoji} {label}: {confidence:.1%}")
        
        with col2:
            sources_count = len(msg.get("sources", []))
            if sources_count > 0:
                st.caption(f"📚 {sources_count} sources")
        
        with col3:
            response_time = msg.get('response_time', 0)
            if response_time > 0:
                st.caption(f"⏱️ {response_time:.1f}s")
        
        # Sources section
        sources = msg.get("sources", [])
        if sources:
            _render_sources_section(sources, index)


def _render_comparison_details(comparison_data: Dict):
    """Render model comparison details with scores."""
    
    with st.expander("🔬 Model Comparison Details", expanded=False):
        st.markdown(f"**🏆 Best Model:** `{comparison_data.get('best_model', 'Unknown')}`")
        st.markdown(f"**📊 Models Compared:** {comparison_data.get('models_compared', 0)}")
        st.markdown(f"**📚 Context Chunks:** {comparison_data.get('context_chunks', 0)}")
        
        st.markdown("---")
        st.markdown("### 📈 Quality Scores")
        
        all_results = comparison_data.get("all_results", [])
        
        for i, result in enumerate(all_results, 1):
            model_name = result.get("model", "Unknown")
            scores = result.get("scores", {})
            
            st.markdown(f"#### Model {i}: `{model_name}`")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                relevance = scores.get("relevance", 0)
                emoji = "🟢" if relevance > 0.7 else "🟡" if relevance > 0.4 else "🔴"
                st.metric("Relevance", f"{relevance:.0%}", help="How relevant is the answer?")
            
            with col2:
                faithfulness = scores.get("faithfulness", 0)
                emoji = "🟢" if faithfulness > 0.7 else "🟡" if faithfulness > 0.4 else "🔴"
                st.metric("Faithfulness", f"{faithfulness:.0%}", help="Is it grounded in context?")
            
            with col3:
                completeness = scores.get("completeness", 0)
                emoji = "🟢" if completeness > 0.7 else "🟡" if completeness > 0.4 else "🔴"
                st.metric("Completeness", f"{completeness:.0%}", help="Does it fully answer?")
            
            with col4:
                overall = scores.get("overall", 0)
                emoji = "🟢" if overall > 0.7 else "🟡" if overall > 0.4 else "🔴"
                st.metric("Overall", f"{overall:.0%}", help="Weighted average score")
            
            # Show generation details
            gen_time = result.get("generation_time", 0)
            tokens = result.get("tokens", {})
            
            if gen_time > 0 or tokens.get("total", 0) > 0:
                detail_col1, detail_col2 = st.columns(2)
                with detail_col1:
                    st.caption(f"⚡ Generation: {gen_time:.3f}s")
                with detail_col2:
                    if tokens.get("total"):
                        st.caption(f"🔢 Tokens: {tokens.get('total', 0)}")
            
            # Show answer preview if not the best model
            if i > 1:
                with st.expander(f"View {model_name} Answer", expanded=False):
                    answer = result.get("answer", "No answer")
                    st.markdown(answer[:500] + ("..." if len(answer) > 500 else ""))
            
            if i < len(all_results):
                st.markdown("---")


def _render_sources_section(sources: List[Dict], msg_index: int):
    """Render sources with previews."""
    
    with st.expander(f"📖 View {len(sources)} Sources", expanded=False):
        for i, src in enumerate(sources, 1):
            doc_name = src.get('document_name', src.get('document', 'Unknown'))
            similarity = src.get('similarity', 0.0)
            
            confidence_emoji = "🎯" if similarity > 0.85 else "✅" if similarity > 0.7 else "⚠️"
            
            st.markdown(f"**{confidence_emoji} {doc_name}** • {similarity:.1%} relevance")
            
            preview = src.get('chunk_preview', src.get('formatted_preview', ''))
            
            if preview and preview.strip():
                cleaned = preview.replace('\\n', '\n')[:500]
                if len(preview) > 500:
                    cleaned += "..."
                
                st.markdown(f"""
                <div style="background-color: #2a2a2a; color: #e0e0e0; padding: 10px; 
                            border-left: 3px solid #00d4aa; font-size: 0.85rem; 
                            border-radius: 4px; margin: 8px 0;">
                    {cleaned}
                </div>
                """, unsafe_allow_html=True)
            
            if src.get('page_number'):
                st.caption(f"📄 Page: {src['page_number']}")
            
            if i < len(sources):
                st.divider()


def _render_chat_input(api):
    """Render the chat input section."""
    
    st.markdown("---")
    
    # Input area
    col1, col2 = st.columns([5, 1])
    
    with col1:
        question = st.text_area(
            "Your question:",
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
        
        # Surprise me button
        if st.button("🎲 Random", use_container_width=True, help="Ask a random question"):
            _handle_surprise_question(api)
    
    # Handle pending question from Surprise Me
    if get_state("pending_question"):
        question = get_state("pending_question")
        set_state("pending_question", None)
        _process_question(api, question)
        return
    
    # Process question on send
    if send_button and question.strip():
        _process_question(api, question.strip())


def _handle_surprise_question(api):
    """Generate and set a random question."""
    try:
        with st.spinner("Generating question..."):
            suggestions = api.generate_suggested_questions(5)
            if suggestions and suggestions.get("questions"):
                import random
                question = random.choice(suggestions["questions"])
                set_state("pending_question", question)
                st.rerun()
            else:
                st.error("No suggestions available. Upload documents first!")
    except Exception as e:
        st.error(f"Failed to generate question: {str(e)}")


def _process_question(api, question: str):
    """Process a user question."""
    
    config = api.get_config() or {}
    comparison_mode = get_state("comparison_mode", False)
    
    # Add user message
    user_msg = {
        "role": "user",
        "content": question,
        "timestamp": time.time()
    }
    
    chat_messages = get_state("chat_messages", [])
    chat_messages.append(user_msg)
    set_state("chat_messages", chat_messages)
    
    # Get response (comparison or standard)
    if comparison_mode:
        with st.spinner("🔬 Comparing models and evaluating responses..."):
            try:
                start_time = time.time()
                
                response = api.compare_models(question, top_k=config.get("TOP_K", 5))
                processing_time = time.time() - start_time
                
                # Format comparison results
                assistant_msg = _format_comparison_response(response, processing_time)
                
            except Exception as e:
                st.error(f"❌ Comparison Error: {str(e)}")
                assistant_msg = {
                    "role": "assistant",
                    "content": f"Sorry, model comparison failed: {str(e)}",
                    "sources": [],
                    "confidence": 0.0,
                    "timestamp": time.time(),
                    "is_comparison": True
                }
    else:
        # Normal mode - single model
        with st.spinner("🔍 Searching documents and generating response..."):
            try:
                start_time = time.time()
                
                response = api.query(question, top_k=config.get("TOP_K", 5))
                processing_time = time.time() - start_time
                
                # Calculate confidence
                sources = response.get("sources", [])
                avg_confidence = 0.0
                if sources:
                    similarities = [src.get('similarity', 0.0) for src in sources]
                    avg_confidence = sum(similarities) / len(similarities)
                
                # Add assistant response
                assistant_msg = {
                    "role": "assistant",
                    "content": response.get("answer", "I couldn't find relevant information."),
                    "sources": sources,
                    "confidence": avg_confidence,
                    "response_time": processing_time,
                    "timestamp": time.time()
                }
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                assistant_msg = {
                    "role": "assistant",
                    "content": f"Sorry, an error occurred: {str(e)}",
                    "sources": [],
                    "confidence": 0.0,
                    "timestamp": time.time()
                }
    
    # Common code for both modes
    chat_messages.append(assistant_msg)
    set_state("chat_messages", chat_messages)
    
    # Update conversation history (for normal mode)
    if not comparison_mode:
        conv_history = get_state("conversation_history", [])
        conv_history.append({
            "question": question,
            "answer": assistant_msg.get("content", ""),
            "confidence": assistant_msg.get("confidence", 0.0)
        })
        set_state("conversation_history", conv_history)
    
    st.rerun()


def _format_comparison_response(response: Dict, processing_time: float) -> Dict:
    """Format model comparison results into a message."""
    
    results = response.get("results", [])
    best_model = response.get("best_model", "Unknown")
    
    if not results:
        return {
            "role": "assistant",
            "content": "No comparison results available.",
            "sources": [],
            "confidence": 0.0,
            "timestamp": time.time(),
            "is_comparison": True
        }
    
    # Use the best model's answer
    best_result = results[0]
    content = best_result.get("answer", "No answer available")
    
    # Extract sources from response
    sources = response.get("sources", [])
    
    # Get scores
    scores = best_result.get("scores", {})
    overall_score = scores.get("overall", 0.0)
    
    return {
        "role": "assistant",
        "content": content,
        "sources": sources,
        "confidence": overall_score,
        "response_time": processing_time,
        "timestamp": time.time(),
        "is_comparison": True,
        "comparison_data": {
            "best_model": best_model,
            "models_compared": len(results),
            "all_results": results,
            "context_chunks": response.get("context_chunks", 0)
        }
    }


def _render_follow_up_suggestions(api):
    """Render follow-up question suggestions."""
    
    chat_messages = get_state("chat_messages", [])
    
    if len(chat_messages) < 2:
        return
    
    st.markdown("---")
    st.markdown("### 💡 Follow-up Suggestions")
    
    suggestions = _generate_contextual_suggestions()
    
    if suggestions:
        cols = st.columns(2)
        
        for i, suggestion in enumerate(suggestions[:4]):
            with cols[i % 2]:
                if st.button(
                    suggestion,
                    key=f"suggestion_{i}",
                    use_container_width=True,
                    help="Click to ask this question"
                ):
                    set_state("pending_question", suggestion)
                    st.rerun()


def _generate_contextual_suggestions() -> List[str]:
    """Generate contextual follow-up suggestions."""
    
    conv_history = get_state("conversation_history", [])
    
    if not conv_history:
        return []
    
    last_question = conv_history[-1].get("question", "").lower()
    
    suggestions = []
    
    # Context-based suggestions
    if any(word in last_question for word in ["what", "define", "explain"]):
        suggestions.extend([
            "Can you provide specific examples?",
            "What are the practical implications?"
        ])
    elif any(word in last_question for word in ["compare", "difference"]):
        suggestions.extend([
            "Which approach is recommended?",
            "What are the trade-offs?"
        ])
    elif any(word in last_question for word in ["how", "process", "method"]):
        suggestions.extend([
            "Are there best practices mentioned?",
            "What resources are needed?"
        ])
    
    # General suggestions
    suggestions.extend([
        "What are the key findings across documents?",
        "Are there any contradictions between sources?"
    ])
    
    return suggestions[:4]
