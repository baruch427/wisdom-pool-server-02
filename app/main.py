from fastapi import FastAPI
from app.endpoints import health, pools, streams, drops
import datetime

app = FastAPI(
    title="Wisdom Pool Server",
    version="0.1.0",
)

# Store startup time
app.state.start_time = datetime.datetime.utcnow()

# Include routers
app.include_router(health.router, tags=["Monitoring"])
app.include_router(pools.router, prefix="/api/v1", tags=["Pools"])
app.include_router(streams.router, prefix="/api/v1", tags=["Streams"])
app.include_router(drops.router, prefix="/api/v1", tags=["Drops"])

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Server is running"}
