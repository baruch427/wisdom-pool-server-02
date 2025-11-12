from firebase_admin import firestore
from fastapi import APIRouter, HTTPException, status, Body, Query
from app.models import (
    Stream, StreamContent, Drop, DropContent, StreamDropPlacement, 
    AddDropResponse, GetDropsResponse, DropInStream, AddDropRequest,
    AddExistingDropRequest, AddExistingDropResponse
)
from app.db import db, streams_collection, drops_collection, stream_drops_collection, pools_collection
import datetime
import uuid
from typing import List, Optional

router = APIRouter()

@router.post("/streams", status_code=status.HTTP_201_CREATED, response_model=Stream)
def create_stream(
    stream_content: StreamContent,
    pool_id: str = Body(..., example="pool_123"),
    creator_id: str = Body(..., example="user_xyz")
):
    """
    Creates a new stream in Firestore.
    """
    # Check if the pool exists
    pool_doc = pools_collection.document(pool_id).get()
    if not pool_doc.exists:
        raise HTTPException(status_code=404, detail=f"Pool with id {pool_id} not found")

    stream_id = str(uuid.uuid4())
    
    new_stream = Stream(
        stream_id=stream_id,
        pool_id=pool_id,
        creator_id=creator_id,
        created_at=datetime.datetime.utcnow(),
        content=stream_content,
        first_drop_placement_id=None,
        last_drop_placement_id=None
    )
    
    streams_collection.document(stream_id).set(new_stream.dict())
    
    return new_stream

@router.get("/streams/{stream_id}", response_model=Stream)
def get_stream(stream_id: str):
    """
    Retrieves stream metadata by its ID.
    """
    doc = streams_collection.document(stream_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Stream not found")
    return doc.to_dict()

@router.post("/streams/{stream_id}/drops", status_code=status.HTTP_201_CREATED, response_model=AddDropResponse)
def add_drop_to_stream(stream_id: str, request: AddDropRequest):
    """
    Adds a new drop to a stream, either at the end or at a specific position.
    This is a transactional operation.
    """
    transaction = db.transaction()

    @firestore.transactional
    def _add_drop(transaction, stream_id, request):
        # ===== PHASE 1: ALL READS MUST HAPPEN FIRST =====
        stream_ref = streams_collection.document(stream_id)
        stream_doc = stream_ref.get(transaction=transaction)

        if not stream_doc.exists:
            raise HTTPException(status_code=404, detail="Stream not found")

        stream_data = stream_doc.to_dict()

        # Determine placement logic and read any required documents
        placement_id = str(uuid.uuid4())
        prev_placement_id = None
        next_placement_id = None
        after_placement_ref = None

        if request.position and request.position.after:
            # Insert after a specific placement - READ first
            after_placement_id = request.position.after
            after_placement_ref = stream_drops_collection.document(
                after_placement_id
            )
            after_placement_doc = after_placement_ref.get(
                transaction=transaction
            )

            if not after_placement_doc.exists:
                raise HTTPException(
                    status_code=404,
                    detail=f"Placement {after_placement_id} not found"
                )
            
            after_placement_data = after_placement_doc.to_dict()
            prev_placement_id = after_placement_id
            next_placement_id = after_placement_data.get('next_placement_id')
        else:
            # Insert at the end of the stream
            prev_placement_id = stream_data.get('last_drop_placement_id')

        # ===== PHASE 2: NOW DO ALL WRITES =====
        # 1. Create the new drop
        drop_id = str(uuid.uuid4())
        new_drop = Drop(
            drop_id=drop_id,
            creator_id=request.creator_id,
            created_at=datetime.datetime.utcnow(),
            content=request.content
        )
        transaction.set(drops_collection.document(drop_id), new_drop.dict())

        # 2. Update placement pointers
        if request.position and request.position.after:
            # Update the 'after' placement's next pointer
            transaction.update(
                after_placement_ref,
                {'next_placement_id': placement_id}
            )

            if next_placement_id:
                # Update the next placement's prev pointer
                next_placement_ref = stream_drops_collection.document(
                    next_placement_id
                )
                transaction.update(
                    next_placement_ref,
                    {'prev_placement_id': placement_id}
                )
            else:
                # This is the new last drop
                transaction.update(
                    stream_ref,
                    {'last_drop_placement_id': placement_id}
                )
        else:
            # Inserting at the end
            if prev_placement_id:
                prev_placement_ref = stream_drops_collection.document(
                    prev_placement_id
                )
                transaction.update(
                    prev_placement_ref,
                    {'next_placement_id': placement_id}
                )
            else:
                # This is the first drop in the stream
                transaction.update(
                    stream_ref,
                    {'first_drop_placement_id': placement_id}
                )
            
            transaction.update(
                stream_ref,
                {'last_drop_placement_id': placement_id}
            )

        # 3. Create the new placement document
        new_placement = StreamDropPlacement(
            placement_id=placement_id,
            stream_id=stream_id,
            drop_id=drop_id,
            next_placement_id=next_placement_id,
            prev_placement_id=prev_placement_id,
            added_at=datetime.datetime.utcnow()
        )
        placement_ref = stream_drops_collection.document(placement_id)
        transaction.set(placement_ref, new_placement.dict())

        # 4. Increment drop count
        transaction.update(stream_ref, {'drop_count': firestore.Increment(1)})

        return AddDropResponse(
            **new_drop.dict(),
            placement_id=placement_id,
            stream_id=stream_id,
            position_info={
                "next_placement_id": next_placement_id,
                "prev_placement_id": prev_placement_id
            }
        )
    
    return _add_drop(transaction, stream_id, request)

@router.get("/streams/{stream_id}/drops", response_model=GetDropsResponse)
def get_drops_in_stream(
    stream_id: str,
    from_placement_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get drops in a stream, with pagination.
    """
    stream_doc = streams_collection.document(stream_id).get()
    if not stream_doc.exists:
        raise HTTPException(status_code=404, detail="Stream not found")

    stream_data = stream_doc.to_dict()
    total_count = stream_data.get('drop_count', 0)
    
    if from_placement_id:
        # Get the document we need to start after
        start_after_doc = stream_drops_collection.document(from_placement_id).get()
        if not start_after_doc.exists:
            raise HTTPException(status_code=404, detail="Starting placement not found")
        
        # Find the next placement in the linked list
        next_placement_id = start_after_doc.to_dict().get('next_placement_id')
        if not next_placement_id:
            return GetDropsResponse(drops=[], has_more=False, total_count=total_count)

        current_placement_doc = stream_drops_collection.document(next_placement_id).get()
    else:
        # Start from the first drop in the stream
        first_placement_id = stream_data.get('first_drop_placement_id')
        if not first_placement_id:
            return GetDropsResponse(drops=[], has_more=False, total_count=total_count)
        
        current_placement_doc = stream_drops_collection.document(first_placement_id).get()

    drops_list = []
    for _ in range(limit):
        if not current_placement_doc or not current_placement_doc.exists:
            break

        placement_data = current_placement_doc.to_dict()
        drop_doc = drops_collection.document(placement_data['drop_id']).get()
        
        if drop_doc.exists:
            drop_data = drop_doc.to_dict()
            drop_in_stream = DropInStream(
                **drop_data,
                placement_id=placement_data['placement_id'],
                next_placement_id=placement_data.get('next_placement_id'),
                prev_placement_id=placement_data.get('prev_placement_id')
            )
            drops_list.append(drop_in_stream)

        # Move to the next drop in the linked list
        next_placement_id = placement_data.get('next_placement_id')
        if next_placement_id:
            current_placement_doc = stream_drops_collection.document(next_placement_id).get()
        else:
            current_placement_doc = None # End of list

    has_more = bool(current_placement_doc and current_placement_doc.exists)

    return GetDropsResponse(drops=drops_list, has_more=has_more, total_count=total_count)

@router.post("/streams/{stream_id}/drops/existing", status_code=status.HTTP_201_CREATED, response_model=AddExistingDropResponse)
def add_existing_drop_to_stream(stream_id: str, request: AddExistingDropRequest):
    """
    Adds an existing drop to a stream. This is a transactional operation.
    """
    transaction = db.transaction()

    @firestore.transactional
    def _add_existing_drop(transaction, stream_id, request):
        stream_ref = streams_collection.document(stream_id)
        stream_doc = stream_ref.get(transaction=transaction)
        if not stream_doc.exists:
            raise HTTPException(status_code=404, detail="Stream not found")

        drop_ref = drops_collection.document(request.drop_id)
        drop_doc = drop_ref.get(transaction=transaction)
        if not drop_doc.exists:
            raise HTTPException(status_code=404, detail="Drop not found")

        stream_data = stream_doc.to_dict()
        
        # Placement logic is identical to adding a new drop
        placement_id = str(uuid.uuid4())
        prev_placement_id = None
        next_placement_id = None

        if request.position and request.position.after:
            after_placement_id = request.position.after
            after_placement_ref = stream_drops_collection.document(after_placement_id)
            after_placement_doc = after_placement_ref.get(transaction=transaction)

            if not after_placement_doc.exists:
                raise HTTPException(status_code=404, detail=f"Placement {after_placement_id} not found")
            
            after_placement_data = after_placement_doc.to_dict()
            prev_placement_id = after_placement_id
            next_placement_id = after_placement_data.get('next_placement_id')

            transaction.update(after_placement_ref, {'next_placement_id': placement_id})

            if next_placement_id:
                next_placement_ref = stream_drops_collection.document(next_placement_id)
                transaction.update(next_placement_ref, {'prev_placement_id': placement_id})
            else:
                transaction.update(stream_ref, {'last_drop_placement_id': placement_id})
        else:
            prev_placement_id = stream_data.get('last_drop_placement_id')
            if prev_placement_id:
                prev_placement_ref = stream_drops_collection.document(prev_placement_id)
                transaction.update(prev_placement_ref, {'next_placement_id': placement_id})
            else:
                transaction.update(stream_ref, {'first_drop_placement_id': placement_id})
            
            transaction.update(stream_ref, {'last_drop_placement_id': placement_id})

        new_placement = StreamDropPlacement(
            placement_id=placement_id,
            stream_id=stream_id,
            drop_id=request.drop_id,
            next_placement_id=next_placement_id,
            prev_placement_id=prev_placement_id,
            added_at=datetime.datetime.utcnow()
        )
        stream_drops_collection.document(placement_id).set(new_placement.dict(), transaction=transaction)

        transaction.update(stream_ref, {'drop_count': firestore.Increment(1)})

        return AddExistingDropResponse(
            placement_id=placement_id,
            stream_id=stream_id,
            drop_id=request.drop_id,
            position_info={
                "next_placement_id": next_placement_id,
                "prev_placement_id": prev_placement_id
            }
        )

    return _add_existing_drop(transaction, stream_id, request)
