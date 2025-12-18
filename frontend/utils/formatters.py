"""Formatting and utility functions."""

from typing import List, Dict, Any
from datetime import datetime


def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def format_sources(sources: List[str]) -> str:
    """Format source list as readable string."""
    if not sources:
        return "No sources"
    return ", ".join(sources[:3])


def get_response_quality(confidence: float) -> str:
    """Get quality indicator based on confidence."""
    if confidence >= 0.8:
        return "🟢 High"
    elif confidence >= 0.6:
        return "🟡 Medium"
    else:
        return "🔴 Low"
