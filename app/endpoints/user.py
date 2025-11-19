from fastapi import APIRouter, Depends, HTTPException
from app.db import users_collection
from app.auth import get_current_user_id
from app.models import (
    UserProgress,
    UserSessionSyncResponse,
    LastActiveContext,
    StreamHistoryEntry,
    UserState,
)
from datetime import datetime, timezone
from app.logger import app_logger

router = APIRouter(prefix="/user")


@router.post("/progress", status_code=204)
async def update_user_progress(
    progress: UserProgress, user_id: str = Depends(get_current_user_id)
):
    """
    Idempotent heartbeat to record where the user is currently looking.
    This updates both the last active context and the specific stream history.
    """
    app_logger.info(f"Updating progress for user {user_id}: {progress}")
    try:
        now = datetime.now(timezone.utc)
        user_state_ref = users_collection.document(user_id).collection("progress").document("main")

        update_data = {
            "last_active_context": {
                "pool_id": progress.pool_id,
                "stream_id": progress.stream_id,
                "drop_id": progress.drop_id,
                "placement_id": progress.placement_id,
                "timestamp": now.isoformat(),
            },
            f"stream_history.{progress.stream_id}": {
                "last_read_drop_id": progress.drop_id,
                "last_read_placement_id": progress.placement_id,
                "updated_at": now.isoformat(),
            },
        }

        # ToDo: Check if the stream is completed and set is_completed flag

        user_state_ref.set(update_data, merge=True)
        app_logger.info(f"Successfully updated progress for user {user_id}")

    except Exception as e:
        app_logger.error(f"Error updating user progress for {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to update user progress.",
        )


@router.get("/session-sync", response_model=UserSessionSyncResponse)
async def get_user_session_sync(user_id: str = Depends(get_current_user_id)):
    """
    Called on application bootstrap to decide where to route the user.
    Returns the last active context or an empty state if no history exists.
    """
    app_logger.info(f"Fetching session sync for user {user_id}")
    try:
        user_state_ref = users_collection.document(user_id).collection("progress").document("main")
        doc = user_state_ref.get()

        if doc.exists:
            user_state = UserState.parse_obj(doc.to_dict())
            app_logger.info(f"Found existing session history for user {user_id}")
            return UserSessionSyncResponse(
                last_active_context=user_state.last_active_context,
                has_history=user_state.last_active_context is not None,
            )
        else:
            app_logger.info(f"No session history found for user {user_id}")
            return UserSessionSyncResponse(last_active_context=None, has_history=False)

    except Exception as e:
        app_logger.error(f"Error getting session sync for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user session data.",
        )
