# Run Both Backend and Frontend

Write-Host "🚀 Starting Resume Analyzer (Backend + Frontend)..." -ForegroundColor Cyan
Write-Host ""

# Start backend in new PowerShell window
Write-Host "📡 Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "d:\4-2\resume-analyzer-python\run-backend.ps1"

# Wait a bit for backend to start
Write-Host "⏳ Waiting for backend to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend in new PowerShell window
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "d:\4-2\resume-analyzer-python\run-frontend.ps1"

Write-Host ""
Write-Host "✅ Both servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend:  http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "📍 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Wait 10-15 seconds for both servers to fully start..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Then open: http://localhost:5173 in your browser" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tip: Check the two new PowerShell windows for server logs" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to close this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
