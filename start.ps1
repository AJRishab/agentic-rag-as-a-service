# Graph RAG Platform - Start Script
# Starts both Backend and Frontend services

Write-Host "🚀 Starting Graph RAG Platform..." -ForegroundColor Green
Write-Host ""

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName "localhost" -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Check if ports are already in use
$backendRunning = Test-Port -Port 8000
$frontendRunning = Test-Port -Port 3000

if ($backendRunning) {
    Write-Host "⚠️  Port 8000 is already in use (Backend may already be running)" -ForegroundColor Yellow
}

if ($frontendRunning) {
    Write-Host "⚠️  Port 3000 is already in use (Frontend may already be running)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📍 Current Directory: $PWD" -ForegroundColor Cyan
Write-Host ""

# Start Backend
if (-not $backendRunning) {
    Write-Host "🐍 Starting Backend Server (FastAPI)..." -ForegroundColor Blue
    $backendPath = Join-Path $PWD "graph-rag-backend"
    Start-Process -WindowStyle Normal powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host '🐍 Graph RAG Backend Server' -ForegroundColor Green; Write-Host 'API: http://localhost:8000' -ForegroundColor Cyan; Write-Host 'Docs: http://localhost:8000/docs' -ForegroundColor Cyan; Write-Host ''; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    
    # Wait for backend to start
    Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 8
}

# Start Frontend
if (-not $frontendRunning) {
    Write-Host "⚛️  Starting Frontend Server (React)..." -ForegroundColor Blue
    $frontendPath = Join-Path $PWD "graph-rag-frontend"
    Start-Process -WindowStyle Normal powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host '⚛️  Graph RAG Frontend Server' -ForegroundColor Green; Write-Host 'App: http://localhost:3000' -ForegroundColor Cyan; Write-Host ''; npm start"
    
    # Wait for frontend to start
    Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

Write-Host ""
Write-Host "🎉 Graph RAG Platform is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access Points:" -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔧 To stop the services:" -ForegroundColor Yellow
Write-Host "   Close the PowerShell windows or press Ctrl+C in each"
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Magenta
Write-Host "   1. Upload documents via the Frontend interface"
Write-Host "   2. Query your knowledge base using natural language"
Write-Host "   3. Check API documentation at /docs endpoint"
Write-Host ""

# Test connectivity after startup
Write-Host "🔍 Testing connectivity..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Write-Host "✅ Backend is healthy!" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not responding yet (may still be starting)" -ForegroundColor Red
}

try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -ErrorAction Stop
    if ($frontendCheck.StatusCode -eq 200) {
        Write-Host "✅ Frontend is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Frontend not responding yet (may still be starting)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🌟 Happy exploring your Graph RAG Platform!" -ForegroundColor Green