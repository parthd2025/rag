#!/bin/bash
# RAG Chatbot Startup Script for Linux/macOS

set -e

echo ""
echo "========================================"
echo "  RAG Chatbot - Startup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org"
    exit 1
fi

# Check if required directories exist
if [ ! -d "backend" ]; then
    echo "ERROR: backend/ directory not found"
    echo "Please ensure you are in the RAG project root directory"
    exit 1
fi

# Install dependencies if needed
echo ""
echo "Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Installing required packages..."
    pip install -r requirements.txt
fi

# Check if model exists
if [ ! -f models/*.gguf ]; then
    echo ""
    echo "WARNING: No GGUF model found in models/ directory"
    echo ""
    echo "Please download a quantized model first:"
    echo "1. Visit: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
    echo "2. Download: mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    echo "3. Place in: models/ directory"
    echo ""
    echo "The application will start but LLM inference will fail without a model."
    echo ""
    read -p "Press Enter to continue..."
fi

echo ""
echo "Starting RAG Backend on http://localhost:8000"
echo ""

# Start backend
cd backend
python3 main.py &
BACKEND_PID=$!

sleep 3

echo ""
echo "Starting RAG Frontend on http://localhost:8501"
echo ""

# Start frontend
cd ../frontend
streamlit run app.py --server.port=8501 &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Both services are starting!"
echo ""
echo "Frontend:  http://localhost:8501"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo "========================================"
echo ""

# Wait for processes
wait
