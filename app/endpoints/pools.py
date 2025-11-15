from fastapi import APIRouter, HTTPException, status, Body
from app.models import Pool, PoolContent
from app.db import pools_collection
import datetime
import uuid
from app.logger import app_logger

router = APIRouter()


@router.post("/pools", status_code=status.HTTP_201_CREATED, response_model=Pool)
def create_pool(
    pool_content: PoolContent, 
    creator_id: str = Body(..., example="user_xyz")
):
    """
    Creates a new pool in Firestore.
    """
    app_logger.info(f"Attempting to create a new pool with title: '{pool_content.title}'")
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
        app_logger.error(f"Failed to retrieve pool {pool_id}: {e}", exc_info=True)
        # Re-raise the original HTTPException if it's a 404, otherwise 500
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Failed to retrieve pool.")
