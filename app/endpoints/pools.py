from fastapi import APIRouter, HTTPException, status, Body
from app.models import Pool, PoolContent
from app.db import pools_collection
import datetime
import uuid

router = APIRouter()


@router.post("/pools", status_code=status.HTTP_201_CREATED, response_model=Pool)
def create_pool(
    pool_content: PoolContent, 
    creator_id: str = Body(..., example="user_xyz")
):
    """
    Creates a new pool in Firestore.
    """
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
    
    return new_pool


@router.get("/pools/{pool_id}", response_model=Pool)
def get_pool(pool_id: str):
    """
    Retrieves a pool by its ID from Firestore.
    """
    doc = pools_collection.document(pool_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Pool not found")
    return doc.to_dict()
