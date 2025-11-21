from fastapi import APIRouter, Depends, HTTPException, Query
from app.db import users_collection
from app.auth import get_current_user_id
from app.models import UserProgress, RiverResponse, RiverRecord
from datetime import datetime, timezone
from app.logger import app_logger
from typing import Optional

router = APIRouter(prefix="/user")


def _parse_timestamp(timestamp: Optional[str]) -> Optional[datetime]:
    """Parse ISO-8601 timestamps while tolerating a trailing Z."""
    if not timestamp:
        return None
    try:
        normalized = timestamp.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


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
        user_state_ref = (
            users_collection.document(user_id)
            .collection("progress")
            .document("main")
        )

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
        app_logger.error(
            f"Error updating user progress for {user_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to update user progress.",
        )


@router.get("/river", response_model=RiverResponse)
async def get_user_river(
    limit: int = Query(30, ge=1, le=30),
    user_id: str = Depends(get_current_user_id),
):
    """Return the user's recent stream history ordered by last activity."""
    app_logger.info(
        f"Fetching river for user {user_id} with limit {limit}"
    )
    try:
        progress_doc = (
            users_collection.document(user_id)
            .collection("progress")
            .document("main")
            .get()
        )

        if not progress_doc.exists:
            app_logger.info(
                f"No progress document found for user {user_id}; "
                "returning empty river"
            )
            return RiverResponse(records=[])

        payload = progress_doc.to_dict() or {}
        stream_history = payload.get("stream_history") or {}

        river_records = []
        for stream_id, history in stream_history.items():
            parsed_timestamp = _parse_timestamp(history.get("updated_at"))
            if not parsed_timestamp:
                app_logger.warning(
                    f"Skipping river record for user {user_id}, stream "
                    f"{stream_id} due to missing timestamp"
                )
                continue

            river_records.append(
                RiverRecord(
                    stream_id=stream_id,
                    last_read_drop_id=history.get("last_read_drop_id"),
                    last_read_placement_id=history.get(
                        "last_read_placement_id"
                    ),
                    updated_at=parsed_timestamp,
                )
            )

        river_records.sort(key=lambda record: record.updated_at, reverse=True)
        trimmed_records = river_records[:limit]

        app_logger.info(
            f"Returning {len(trimmed_records)} river records for user "
            f"{user_id}"
        )
        return RiverResponse(records=trimmed_records)

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(
            f"Error retrieving river for user {user_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to load user river.",
        )


