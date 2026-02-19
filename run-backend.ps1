# Run Backend Server

Write-Host "🚀 Starting Resume Analyzer Backend..." -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Set-Location -Path "d:\4-2\resume-analyzer-python\resume-analyzer-backend"

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "📦 Installing/Updating dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "✅ Dependencies installed!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Starting backend server..." -ForegroundColor Cyan
Write-Host "📍 Backend URL: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "📚 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Run the server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
