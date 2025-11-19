# This script automates the process of running the integration tests.
# 1. Starts the Docker test environment in detached mode.
# 2. Waits for services to initialize.
# 3. Runs the pytest suite.
# 4. Shuts down and cleans up the Docker environment, regardless of test outcome.

# Stop on any error
$ErrorActionPreference = "Stop"

# Check if Docker is running
docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker Desktop is not running." -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host "--- Starting Test Environment (Docker Compose) ---" -ForegroundColor Green
# Start containers in detached mode
docker-compose -f ztest/docker-compose.automated.yml up --build -d

# Wait for services to become healthy. 10 seconds is usually enough for local startup.
Write-Host "--- Waiting 10 seconds for services to initialize... ---" -ForegroundColor Cyan
Start-Sleep -Seconds 10

$pytest_exit_code = 0
try {
    Write-Host "--- Running Pytest Integration Tests inside the container ---" -ForegroundColor Green
    
    # Execute pytest inside the 'app' container with PYTHONPATH set
    docker-compose -f ztest/docker-compose.automated.yml exec -e PYTHONPATH=/code app pytest -v ztest/
    
    # Capture the exit code from the docker-compose command
    $pytest_exit_code = $LASTEXITCODE
}
finally {
    # This 'finally' block ensures that cleanup always happens.
    Write-Host "--- Shutting Down and Cleaning Up Test Environment ---" -ForegroundColor Yellow
    docker-compose -f ztest/docker-compose.automated.yml down
}

# Provide a clear final status message
if ($pytest_exit_code -ne 0) {
    Write-Host "--- Tests FAILED ---" -ForegroundColor Red
} else {
    Write-Host "--- All Tests Passed Successfully! ---" -ForegroundColor Green
}

# Exit the script with the same exit code as pytest, which is useful for CI/CD systems.
exit $pytest_exit_code
