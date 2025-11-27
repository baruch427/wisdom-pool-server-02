from fastapi import APIRouter, Depends, HTTPException, Query
from app.db import users_collection
from app.auth import get_current_user_id
from app.models import UserProgress, RiverResponse, RiverRecord
from datetime import datetime, timezone
from app.logger import app_logger
from typing import Any, Optional

router = APIRouter(prefix="/user")


def _parse_timestamp(timestamp: Optional[Any]) -> Optional[datetime]:
    """Normalize Firestore/native timestamps into aware datetimes."""
    if timestamp is None:
        return None

    if isinstance(timestamp, datetime):
        return (
            timestamp
            if timestamp.tzinfo
            else timestamp.replace(tzinfo=timezone.utc)
        )

    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    if isinstance(timestamp, str):
        try:
            normalized = timestamp.replace("Z", "+00:00")
            dt_value = datetime.fromisoformat(normalized)
            return (
                dt_value
                if dt_value.tzinfo
                else dt_value.replace(tzinfo=timezone.utc)
            )
        except ValueError:
            return None

    return None


@router.post("/progress", status_code=204)
def update_user_progress(
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
                "placement_id": progress.placement_id,
                "timestamp": now,
            },
            f"stream_history.{progress.stream_id}": {
                "last_read_placement_id": progress.placement_id,
                "updated_at": now,
            },
        }

        # ToDo: Check if the stream is completed and set is_completed flag

        # Create document if it doesn't exist, then update
        if not user_state_ref.get().exists:
            user_state_ref.set({})
        user_state_ref.update(update_data)
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
def get_user_river(
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

        # Firestore may materialize dotted field names (stream_history.<id>)
        # when the document was created via a merged set. Fold those back into
        # the stream_history map so older records remain visible.
        for key, value in payload.items():
            if not key.startswith("stream_history."):
                continue
            stream_id = key.split("stream_history.", 1)[1]
            if stream_id and stream_id not in stream_history:
                stream_history[stream_id] = value

        river_records = []
        fallback_timestamp = datetime.min.replace(tzinfo=timezone.utc)
        for stream_id, history in stream_history.items():
            parsed_timestamp = _parse_timestamp(history.get("updated_at"))
            if not parsed_timestamp:
                app_logger.warning(
                    f"Falling back to sentinel timestamp for user {user_id}, "
                    f"stream {stream_id} due to missing/invalid updated_at"
                )
                parsed_timestamp = fallback_timestamp

            river_records.append(
                RiverRecord(
                    stream_id=stream_id,
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


