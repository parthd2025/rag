# RAG Chatbot - Run Backend and Frontend
# This script starts both services in separate windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RAG Chatbot - Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

Write-Host "Starting Backend on http://localhost:8001..." -ForegroundColor Green
$backendPath = Join-Path $PWD "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$backendPath`"; python main.py"

Start-Sleep -Seconds 3

Write-Host "Starting Frontend on http://localhost:8501..." -ForegroundColor Green
$frontendPath = Join-Path $PWD "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd `"$frontendPath`"; streamlit run app.py"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Services Starting!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend:  http://localhost:8501" -ForegroundColor Yellow
Write-Host "Backend:   http://localhost:8001" -ForegroundColor Yellow
Write-Host "API Docs:  http://localhost:8001/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Close the PowerShell windows to stop the services." -ForegroundColor Gray
Write-Host ""

