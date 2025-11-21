from typing import Optional

from fastapi import APIRouter, HTTPException, status, Body, Query

from app.models import (
    Pool,
    PoolContent,
    PoolListResponse,
)
from app.db import pools_collection
import datetime
import uuid
from app.logger import app_logger


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


@router.get("/pools", response_model=PoolListResponse)
def list_pools(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    creator_id: Optional[str] = Query(None),
):
    """Returns pools with optional creator filtering and pagination."""

    app_logger.info(
        "Listing pools with limit=%s offset=%s creator_id=%s",
        limit,
        offset,
        creator_id,
    )

    try:
        query = pools_collection
        if creator_id:
            query = query.where("creator_id", "==", creator_id)

        total_count = len(list(query.stream()))

        ordered_query = query.order_by("created_at")
        if offset:
            ordered_query = ordered_query.offset(offset)

        pool_docs = ordered_query.limit(limit).stream()
        pools = [Pool(**doc.to_dict()) for doc in pool_docs]

        next_offset = offset + len(pools)
        has_more = next_offset < total_count

        return PoolListResponse(
            pools=pools,
            total_count=total_count,
            has_more=has_more,
            next_offset=next_offset if has_more else None,
        )
    except Exception as e:
        app_logger.error("Failed listing pools: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list pools.")


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
