"""
Process Flow Status Component - Displays horizontal flow with status indicators.
"""

import streamlit as st
from typing import List, Dict, Optional

def render_process_flow(processes: List[Dict[str, any]]) -> None:
    """
    Render a horizontal process flow with status indicators.
    
    Args:
        processes: List of process dictionaries with keys:
                  - name (str): Process name
                  - status (str): 'pending', 'success', 'error', 'processing'
                  
    Example:
        processes = [
            {"name": "Upload", "status": "success"},
            {"name": "Process", "status": "processing"},
            {"name": "Index", "status": "pending"},
            {"name": "Ready", "status": "pending"}
        ]
        render_process_flow(processes)
    """
    
    # CSS for styling the flow
    st.markdown("""
    <style>
    .process-flow-container {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 8px;
        padding: 10px;
        background: linear-gradient(90deg, transparent 0%, #f0f2f6 100%);
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    .process-step {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
    }
    
    .process-step.pending {
        background-color: #e0e0e0;
        color: #666;
    }
    
    .process-step.pending::after {
        content: "◯";
        font-size: 14px;
        margin-left: 4px;
    }
    
    .process-step.processing {
        background-color: #fff3cd;
        color: #856404;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    .process-step.processing::after {
        content: "⟳";
        font-size: 14px;
        margin-left: 4px;
        animation: spin 1.5s linear infinite;
    }
    
    .process-step.success {
        background-color: #d4edda;
        color: #155724;
    }
    
    .process-step.success::after {
        content: "✓";
        font-size: 14px;
        margin-left: 4px;
        color: #28a745;
        font-weight: bold;
    }
    
    .process-step.error {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .process-step.error::after {
        content: "✕";
        font-size: 14px;
        margin-left: 4px;
        color: #dc3545;
        font-weight: bold;
    }
    
    .process-step.separator {
        padding: 0 2px;
        color: #ccc;
        font-size: 10px;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Build HTML for flow
    flow_html = '<div class="process-flow-container">'
    
    for idx, process in enumerate(processes):
        status = process.get("status", "pending")
        name = process.get("name", "Step")
        
        flow_html += f'<div class="process-step {status}">{name}</div>'
        
        # Add separator between steps (except after last)
        if idx < len(processes) - 1:
            flow_html += '<div class="process-step separator">→</div>'
    
    flow_html += '</div>'
    
    st.markdown(flow_html, unsafe_allow_html=True)


def update_process_status(process_name: str, status: str) -> None:
    """
    Update the status of a specific process in session state.
    
    Args:
        process_name: Name of the process to update
        status: New status ('pending', 'processing', 'success', 'error')
    """
    if "process_flow" not in st.session_state:
        st.session_state.process_flow = []
    
    # Find and update the process
    for process in st.session_state.process_flow:
        if process["name"] == process_name:
            process["status"] = status
            break


def initialize_process_flow(processes: List[str]) -> None:
    """
    Initialize the process flow in session state.
    
    Args:
        processes: List of process names
    """
    if "process_flow" not in st.session_state:
        st.session_state.process_flow = [
            {"name": p, "status": "pending"} for p in processes
        ]


def get_process_flow() -> List[Dict[str, any]]:
    """
    Get the current process flow from session state.
    
    Returns:
        List of process dictionaries
    """
    if "process_flow" not in st.session_state:
        st.session_state.process_flow = []
    
    return st.session_state.process_flow
