# This script starts the development server with REAL Firebase connection.
# Perfect for:
# - Manual API testing with real data
# - Running custom scripts (see scripts/ directory)
# - Viewing data in Firebase Console (https://console.firebase.google.com)
# - No Java/emulator required

# Check if Docker is running (suppress all output)
try {
    $ErrorActionPreference = "SilentlyContinue"
    $null = docker info 2>&1
    $dockerRunning = $LASTEXITCODE -eq 0
    $ErrorActionPreference = "Stop"
    
    if (-not $dockerRunning) {
        Write-Host "Error: Docker Desktop is not running." -ForegroundColor Red
        Write-Host "Please start Docker Desktop and try again." -ForegroundColor Red
        exit 1
    }
} catch {
    $ErrorActionPreference = "Stop"
    Write-Host "Error: Docker Desktop is not running." -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Stop on any error from here on
$ErrorActionPreference = "Stop"

Write-Host "--- Starting Development Server with Real Firebase ---" -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Documentation at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "View database at: https://console.firebase.google.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can run custom scripts in another terminal:" -ForegroundColor Yellow
Write-Host "  python scripts/example_script.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Start the container with logs attached
docker-compose -f docker-compose.dev.yml up --build
