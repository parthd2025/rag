@echo off
REM RAG Chatbot Startup Script for Windows

echo.
echo ========================================
echo   RAG Chatbot - Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if required directories exist
if not exist "backend\" (
    echo ERROR: backend\ directory not found
    echo Please ensure you are in the RAG project root directory
    pause
    exit /b 1
)

REM Install dependencies if needed
echo.
echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if model exists
if not exist "models\*.gguf" (
    echo.
    echo WARNING: No GGUF model found in models\ directory
    echo.
    echo Please download a quantized model first:
    echo 1. Visit: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
    echo 2. Download: mistral-7b-instruct-v0.2.Q4_K_M.gguf
    echo 3. Place in: models\ directory
    echo.
    echo The application will start but LLM inference will fail without a model.
    echo.
    pause
)

echo.
echo Starting RAG Backend on http://localhost:8001
echo.

REM Start backend in new window
start "RAG Backend" /D backend python main.py

timeout /t 3 /nobreak

echo.
echo Starting RAG Frontend on http://localhost:8501
echo.

REM Start frontend
start "RAG Frontend" /D frontend streamlit run app.py --server.port=8501

echo.
echo ========================================
echo Both services are starting!
echo.
echo Frontend:  http://localhost:8501
echo Backend:   http://localhost:8001
echo API Docs:  http://localhost:8001/docs
echo.
echo Close either window to stop that service.
echo ========================================
echo.

pause
