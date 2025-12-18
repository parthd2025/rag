"""Conversation history persistence."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
import streamlit as st


class ConversationManager:
    """Manage conversation history storage and retrieval."""
    
    def __init__(self, storage_dir: str = ".streamlit/conversations"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_conversation(self, conversation_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Save conversation to file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
            
            data = {
                "id": conversation_id,
                "created": datetime.now().isoformat(),
                "message_count": len(messages),
                "messages": messages
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            st.error(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Load conversation from file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    return data.get("messages", [])
            return []
        except Exception as e:
            st.error(f"Error loading conversation: {e}")
            return []
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all saved conversations."""
        conversations = []
        
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.storage_dir, filename)
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        conversations.append({
                            "id": data["id"],
                            "created": data["created"],
                            "message_count": data["message_count"]
                        })
        except Exception as e:
            st.error(f"Error listing conversations: {e}")
        
        return sorted(conversations, key=lambda x: x["created"], reverse=True)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        try:
            file_path = os.path.join(self.storage_dir, f"{conversation_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            st.error(f"Error deleting conversation: {e}")
            return False
    
    def export_conversation(self, conversation_id: str, format: str = "json") -> str:
        """Export conversation in specified format."""
        messages = self.load_conversation(conversation_id)
        
        if format == "json":
            return json.dumps(messages, indent=2)
        elif format == "txt":
            lines = []
            for msg in messages:
                lines.append(f"{msg['role'].upper()}: {msg['content']}")
                if msg.get("sources"):
                    lines.append(f"  Sources: {', '.join(msg['sources'])}")
            return "\n\n".join(lines)
        elif format == "markdown":
            lines = []
            for msg in messages:
                if msg["role"] == "user":
                    lines.append(f"**User:** {msg['content']}")
                else:
                    lines.append(f"**Assistant:** {msg['content']}")
                if msg.get("sources"):
                    lines.append(f"\n*Sources: {', '.join(msg['sources'])}*\n")
            return "\n\n".join(lines)
        
        return ""


@st.cache_resource
def get_conversation_manager() -> ConversationManager:
    """Get cached conversation manager instance."""
    return ConversationManager()
