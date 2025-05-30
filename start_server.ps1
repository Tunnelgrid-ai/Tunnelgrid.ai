# AI Brand Analysis - Server Startup Script
# This script activates the virtual environment and starts the FastAPI server

Write-Host "🚀 Starting AI Brand Analysis Backend..." -ForegroundColor Green
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow

# Activate virtual environment
& ".\\.venv\\Scripts\\Activate.ps1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "💡 Make sure you're in the project root directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host "🌐 Starting server on http://127.0.0.1:8000..." -ForegroundColor Yellow

# Start the server using the Python startup script
python start_server.py 