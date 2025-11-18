from fastapi import APIRouter, HTTPException, status, Body, Depends
from app.models import (
    Pool,
    PoolContent,
    RiverFeedResponse,
    StreamWithProgress,
    UserStreamProgress,
)
from app.db import db, pools_collection, streams_collection
import datetime
import uuid
from app.logger import app_logger
from typing import Optional
from app.auth import get_current_user_id


router = APIRouter()


@router.post(
    "/pools", status_code=status.HTTP_201_CREATED, response_model=Pool
)
def create_pool(
    pool_content: PoolContent,
    creator_id: str = Body(..., example="user_xyz"),
):
    """
    Creates a new pool in Firestore.
    """
    app_logger.info(
        f"Attempting to create a new pool with title: '{pool_content.title}'"
    )
    try:
        # Generate a unique ID for the new pool
        pool_id = str(uuid.uuid4())
        
        new_pool = Pool(
            pool_id=pool_id,
            creator_id=creator_id,
            created_at=datetime.datetime.utcnow(),
            content=pool_content
        )
        
        # Save the new pool to Firestore
        pools_collection.document(pool_id).set(new_pool.dict())
        
        app_logger.info(f"Successfully created pool with ID: {pool_id}")
        return new_pool
    except Exception as e:
        app_logger.error(f"Failed to create pool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create pool.")


@router.get("/pools/{pool_id}", response_model=Pool)
def get_pool(pool_id: str):
    """
    Retrieves a pool by its ID from Firestore.
    """
    app_logger.info(f"Attempting to retrieve pool with ID: {pool_id}")
    try:
        doc = pools_collection.document(pool_id).get()
        if not doc.exists:
            app_logger.warning(f"Pool with ID {pool_id} not found.")
            raise HTTPException(status_code=404, detail="Pool not found")
        
        app_logger.info(f"Successfully retrieved pool with ID: {pool_id}")
        return doc.to_dict()
    except Exception as e:
        app_logger.error(
            f"Failed to retrieve pool {pool_id}: {e}", exc_info=True
        )
        # Re-raise the original HTTPException if it's a 404, otherwise 500
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Failed to retrieve pool.")


@router.get(
    "/pools/{pool_id}/river",
    response_model=RiverFeedResponse,
    dependencies=[Depends(get_current_user_id)],
)
async def get_river_feed(
    pool_id: str,
    user_id: str = Depends(get_current_user_id),
    cursor: Optional[str] = None,
    limit: int = 5,
):
    """
    Fetches the vertical list of streams for the main view,
    joined with user progress.
    """
    try:
        # 1. Query Streams collection for the given pool
        streams_query = (
            streams_collection.where("pool_id", "==", pool_id)
            .order_by("created_at")
            .limit(limit)
        )
        if cursor:
            cursor_doc = streams_collection.document(cursor).get()
            if not cursor_doc.exists:
                raise HTTPException(status_code=404, detail="Cursor not found")
            streams_query = streams_query.start_after(cursor_doc)

        stream_docs = streams_query.stream()
        streams = [doc.to_dict() for doc in stream_docs]

        # 2. Fetch the UserState document for the requesting user
        user_state_doc = (
            db.collection("user_state")
            .document(user_id)
            .collection("progress")
            .document("main")
            .get()
        )
        user_state = (
            user_state_doc.to_dict() if user_state_doc.exists else {}
        )
        stream_history = user_state.get("stream_history", {})

        # 3. Join Data
        streams_with_progress = []
        for stream in streams:
            stream_id = stream["stream_id"]
            progress = stream_history.get(stream_id, {})
            user_progress = UserStreamProgress(
                last_read_placement_id=progress.get("last_read_placement_id"),
                is_completed=progress.get("is_completed", False),
            )
            streams_with_progress.append(
                StreamWithProgress(**stream, user_progress=user_progress)
            )

        # 4. Determine the next cursor
        next_cursor = None
        if len(streams) == limit:
            last_stream_id = streams[-1]["stream_id"]
            next_cursor = last_stream_id

        return RiverFeedResponse(
            streams=streams_with_progress, next_cursor=next_cursor
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        app_logger.error(f"Failed to get river feed for pool {pool_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get river feed."
        )
