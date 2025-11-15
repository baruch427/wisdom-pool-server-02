from fastapi import APIRouter, HTTPException
from app.models import Drop
from app.db import drops_collection
from app.logger import app_logger

router = APIRouter()

@router.get("/drops/{drop_id}", response_model=Drop)
def get_drop(drop_id: str):
    """
    Retrieves a single drop by its ID from Firestore.
    """
    app_logger.info(f"Attempting to retrieve drop with ID: {drop_id}")
    try:
        doc = drops_collection.document(drop_id).get()
        if not doc.exists:
            app_logger.warning(f"Drop with ID {drop_id} not found.")
            raise HTTPException(status_code=404, detail="Drop not found")
        
        app_logger.info(f"Successfully retrieved drop with ID: {drop_id}")
        return doc.to_dict()
    except Exception as e:
        app_logger.error(f"Failed to retrieve drop {drop_id}: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Failed to retrieve drop.")
