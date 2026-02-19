# Run Frontend Server

Write-Host "🎨 Starting Resume Analyzer Frontend..." -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Set-Location -Path "d:\4-2\resume-analyzer-python\resume-analyzer-frontend"

# Check if node_modules exists
if (-Not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Dependencies installed!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "🌐 Starting frontend dev server..." -ForegroundColor Cyan
Write-Host "📍 Frontend URL: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Make sure backend is running on http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Run the dev server
npm run dev
