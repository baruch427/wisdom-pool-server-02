from fastapi import APIRouter, Request
from app.models import HealthStatus
import datetime

router = APIRouter()

@router.get("/health", response_model=HealthStatus)
def get_health(request: Request):
    """
    Returns the server's health status, including startup time.
    """
    # In a real scenario, you might get the commit hash from an environment variable
    # set during the build process.
    commit_hash = "local-dev" 
    
    return {
        "status": "ok",
        "start_time_utc": request.app.state.start_time.isoformat(),
        "server_time_utc": datetime.datetime.utcnow().isoformat(),
        "commit_hash": commit_hash
    }
