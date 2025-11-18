from fastapi import FastAPI, Response
from app.endpoints import health, pools, streams, drops, user, river
import datetime
from app.logger import app_logger, log_stream


app = FastAPI(
    title="Wisdom Pool Server",
    version="1.3",
)

# Store startup time
app.state.start_time = datetime.datetime.utcnow()

# Include routers
app.include_router(health.router, tags=["Monitoring"])
app.include_router(pools.router, prefix="/api/v1", tags=["Pools"])
app.include_router(streams.router, prefix="/api/v1", tags=["Streams"])
app.include_router(drops.router, prefix="/api/v1", tags=["Drops"])
app.include_router(user.router, prefix="/api/v1", tags=["User"])
app.include_router(river.router, prefix="/api/v1/pools", tags=["River"])


@app.get("/logs", include_in_schema=False)
def get_logs():
    """Returns the content of the in-memory log."""
    log_content = log_stream.getvalue()
    return Response(content=log_content, media_type="text/plain")


@app.delete("/logs/clear", include_in_schema=False)
def clear_logs():
    """Clears the in-memory log."""
    log_stream.truncate(0)
    log_stream.seek(0)
    app_logger.info("Log cleared.")
    return {"message": "Log cleared."}


@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Server is running"}
