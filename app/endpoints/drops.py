from fastapi import APIRouter, HTTPException
from app.models import Drop
from app.db import drops_collection

router = APIRouter()

@router.get("/drops/{drop_id}", response_model=Drop)
def get_drop(drop_id: str):
    """
    Retrieves a single drop by its ID from Firestore.
    """
    doc = drops_collection.document(drop_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Drop not found")
    return doc.to_dict()
