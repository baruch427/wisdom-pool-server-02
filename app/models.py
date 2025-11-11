from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class PoolContent(BaseModel):
    title: str = Field(..., example="The Nature of Consciousness")
    description: str = Field(..., example="A curated collection of thoughts and resources exploring consciousness.")

class Pool(BaseModel):
    pool_id: str = Field(..., example="pool_123")
    creator_id: str = Field(..., example="user_abc")
    created_at: datetime
    content: PoolContent

class StreamContent(BaseModel):
    title: str = Field(..., example="Exploring Quantum Mechanics")
    description: str = Field(..., example="A stream of thoughts on quantum physics.")
    ai_framing: Optional[str] = Field(None, example="This stream is framed as a journey from classical to quantum physics.")
    category: Optional[str] = Field(None, example="Science")
    image: Optional[str] = Field(None, example="https://example.com/image.jpg")

class Stream(BaseModel):
    stream_id: str = Field(..., example="stream_456")
    pool_id: str = Field(..., example="pool_123")
    creator_id: str = Field(..., example="user_abc")
    created_at: datetime
    first_drop_placement_id: Optional[str] = Field(None, example="placement_789")
    last_drop_placement_id: Optional[str] = Field(None, example="placement_987")
    content: StreamContent

class DropContent(BaseModel):
    title: Optional[str] = Field(None, example="What is superposition?")
    text: str = Field(..., example="Superposition is a fundamental principle of quantum mechanics.")
    images: Optional[List[str]] = Field(None, example=["https://example.com/superposition.jpg"])
    type: Optional[str] = Field("text", example="text")

class Drop(BaseModel):
    drop_id: str = Field(..., example="drop_abc")
    creator_id: str = Field(..., example="user_abc")
    created_at: datetime
    content: DropContent

class StreamDropPlacement(BaseModel):
    placement_id: str = Field(..., example="placement_789")
    stream_id: str = Field(..., example="stream_456")
    drop_id: str = Field(..., example="drop_abc")
    next_placement_id: Optional[str] = None
    prev_placement_id: Optional[str] = None
    added_at: datetime

class AddDropResponse(Drop):
    placement_id: str
    stream_id: str
    position_info: dict

class DropInStream(Drop):
    placement_id: str
    next_placement_id: Optional[str] = None
    prev_placement_id: Optional[str] = None

class GetDropsResponse(BaseModel):
    drops: List[DropInStream]
    has_more: bool
    total_count: int

class HealthStatus(BaseModel):
    status: str
    start_time_utc: str
    server_time_utc: str
    commit_hash: str
