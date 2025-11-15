# This script starts the local development server for manual testing.
# It uses the docker-compose.manual.yml file with hot-reload enabled.

# Stop on any error
$ErrorActionPreference = "Stop"

Write-Host "--- Starting Test Environment with Emulator (Docker Compose) ---" -ForegroundColor Green
Write-Host "The server will be available at http://localhost:8000"
Write-Host "The interactive API docs (Swagger UI) will be at http://localhost:8000/docs"
Write-Host "Note: Requires Java 21+ for Firestore emulator" -ForegroundColor Yellow
Write-Host "Press CTRL+C to stop the server." -ForegroundColor Yellow

# Start containers and attach to the logs.
# --build ensures the image is updated if Dockerfile or requirements change.
docker-compose -f ztest/docker-compose.manual.yml up --build
