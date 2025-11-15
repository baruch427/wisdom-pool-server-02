from fastapi import APIRouter, Request, HTTPException
from app.models import HealthStatus
import datetime
from app.logger import app_logger

router = APIRouter()

@router.get("/health", response_model=HealthStatus)
def get_health(request: Request):
    """
    Returns the server's health status, including startup time.
    """
    try:
        app_logger.info("Health check requested.")
        # In a real scenario, you might get the commit hash from an environment variable
        # set during the build process.
        commit_hash = "local-dev" 
        
        status = {
            "status": "ok",
            "start_time_utc": request.app.state.start_time.isoformat(),
            "server_time_utc": datetime.datetime.utcnow().isoformat(),
            "commit_hash": commit_hash
        }
        app_logger.info("Health check successful.")
        return status
    except Exception as e:
        app_logger.error(f"Error during health check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during health check.")
