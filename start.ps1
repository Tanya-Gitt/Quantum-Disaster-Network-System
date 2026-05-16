# Quick-start script for Windows (PowerShell)
# Requires: Docker Desktop running

Write-Host "Starting Quantum Disaster Network..." -ForegroundColor Cyan

# Check Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker not found. Install Docker Desktop from https://docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

$running = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Desktop is not running. Please start it." -ForegroundColor Red
    exit 1
}

Write-Host "Building and starting all services..." -ForegroundColor Green
docker compose up --build -d

Write-Host ""
Write-Host "Services starting up. URLs:" -ForegroundColor Cyan
Write-Host "  Dashboard:   http://localhost:3000" -ForegroundColor White
Write-Host "  API:         http://localhost:5000/api/health" -ForegroundColor White
Write-Host "  AI Engine:   http://localhost:5001/health" -ForegroundColor White
Write-Host "  PQC Service: http://localhost:5002/health" -ForegroundColor White
Write-Host "  Mesh Sim:    http://localhost:5003/health" -ForegroundColor White
Write-Host "  Blockchain:  http://localhost:5004/health" -ForegroundColor White
Write-Host ""
Write-Host "To stop: docker compose down" -ForegroundColor Yellow
