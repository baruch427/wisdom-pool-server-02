from pydantic import BaseModel, Field
from datetime import datetime

class PoolContent(BaseModel):
    title: str = Field(..., example="The Nature of Consciousness")
    description: str = Field(..., example="A curated collection of thoughts and resources exploring consciousness.")

class Pool(BaseModel):
    pool_id: str = Field(..., example="pool_123")
    creator_id: str = Field(..., example="user_abc")
    created_at: datetime
    content: PoolContent

class HealthStatus(BaseModel):
    status: str
    start_time_utc: str
    server_time_utc: str
    commit_hash: str
