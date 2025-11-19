from fastapi import APIRouter, Depends, HTTPException, status
from app.db import streams_collection, db
from app.auth import get_current_user_id
from app.models import (
    Stream,
    StreamWithProgress,
    RiverFeedResponse,
    UserState,
    UserStreamProgress,
)
from typing import List, Optional
from app.logger import app_logger

router = APIRouter()


@router.get("/{pool_id}/river", response_model=RiverFeedResponse)
async def get_river_feed(
    pool_id: str,
    user_id: str = Depends(get_current_user_id),
    cursor: Optional[str] = None,
    limit: int = 5,
):
    """
    Fetches the vertical list of streams for the main view, joined with user progress.
    """
    app_logger.info(f"Fetching river feed for pool {pool_id}, user {user_id}, cursor={cursor}, limit={limit}")
    try:
        # 1. Query Streams for the given pool
        query = streams_collection.where("pool_id", "==", pool_id).limit(limit)
        if cursor:
            cursor_doc = streams_collection.document(cursor).get()
            if not cursor_doc.exists:
                app_logger.warning(f"Cursor document {cursor} not found for river feed")
                raise HTTPException(status_code=404, detail="Cursor document not found")
            query = query.start_after(cursor_doc)

        stream_docs = query.stream()
        streams = [Stream(**doc.to_dict()) for doc in stream_docs]

        # 2. Fetch UserState for the requesting user
        user_state_doc = db.collection("users").document(user_id).collection("progress").document("main").get()
        user_state = UserState.parse_obj(user_state_doc.to_dict()) if user_state_doc.exists else UserState()

        # 3. Join Data
        streams_with_progress: List[StreamWithProgress] = []
        for stream in streams:
            progress_data = user_state.stream_history.get(stream.stream_id)
            user_progress = UserStreamProgress()
            if progress_data:
                user_progress.last_read_placement_id = progress_data.last_read_placement_id
                user_progress.is_completed = progress_data.is_completed
            
            stream_with_progress = StreamWithProgress(
                **stream.dict(),
                user_progress=user_progress
            )
            streams_with_progress.append(stream_with_progress)

        # Determine the next cursor
        next_cursor_val = streams_with_progress[-1].stream_id if len(streams_with_progress) == limit else None

        app_logger.info(f"Successfully retrieved {len(streams_with_progress)} streams for river feed")
        return RiverFeedResponse(streams=streams_with_progress, next_cursor=next_cursor_val)

    except Exception as e:
        app_logger.error(f"Error getting river feed for pool {pool_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve river feed.",
        )