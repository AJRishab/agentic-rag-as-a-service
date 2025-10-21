# Graph RAG Platform - Simple Start Script
Write-Host "Starting Graph RAG Platform..." -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "Starting Backend Server (FastAPI)..." -ForegroundColor Blue
$backendPath = Join-Path $PWD "graph-rag-backend"
Start-Process -WindowStyle Normal powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host 'Backend Server Starting...'; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Start Frontend
Write-Host "Starting Frontend Server (React)..." -ForegroundColor Blue
$frontendPath = Join-Path $PWD "graph-rag-frontend"
Start-Process -WindowStyle Normal powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'Frontend Server Starting...'; npm start"

# Wait for frontend to start
Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Graph RAG Platform is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# Test connectivity
Write-Host "Testing connectivity..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -ErrorAction Stop
    Write-Host "Backend is healthy!" -ForegroundColor Green
} catch {
    Write-Host "Backend not responding yet (may still be starting)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Setup complete! Check your browser at http://localhost:3000" -ForegroundColor Green