from fastapi import APIRouter, HTTPException, status, Body, Query
from app.models import (
    Stream, StreamContent, Drop, DropContent, StreamDropPlacement,
    AddDropResponse, GetDropsResponse, DropInStream, AddDropsResponse
)
from app.db import (
    db, streams_collection, drops_collection,
    stream_drops_collection, pools_collection
)
from firebase_admin import firestore
import datetime
import uuid
from typing import List, Optional, Union
from app.logger import app_logger


router = APIRouter()


@router.post(
    "/streams",
    status_code=status.HTTP_201_CREATED,
    response_model=Stream
)
def create_stream(
    stream_content: StreamContent,
    pool_id: str = Body(..., example="pool_123"),
    creator_id: str = Body(..., example="user_xyz")
):
    """
    Creates a new stream in Firestore.
    """
    app_logger.info(f"Attempting to create stream in pool {pool_id}")
    try:
        # Check if the pool exists
        pool_doc = pools_collection.document(pool_id).get()
        if not pool_doc.exists:
            raise HTTPException(
                status_code=404, detail=f"Pool with id {pool_id} not found"
            )

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
        app_logger.info(f"Successfully created stream {stream_id} in pool {pool_id}")
        return new_stream
    except Exception as e:
        app_logger.error(f"Failed to create stream in pool {pool_id}: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Failed to create stream.")


@router.get("/streams/{stream_id}", response_model=Stream)
def get_stream(stream_id: str):
    """
    Retrieves stream metadata by its ID.
    """
    app_logger.info(f"Attempting to retrieve stream {stream_id}")
    try:
        doc = streams_collection.document(stream_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Stream not found")
        app_logger.info(f"Successfully retrieved stream {stream_id}")
        return doc.to_dict()
    except Exception as e:
        app_logger.error(f"Failed to retrieve stream {stream_id}: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Failed to retrieve stream.")


def _add_drops_transactional(transaction, stream_id, drops, creator_id):
    """
    This function runs within a Firestore transaction to add drops to a stream.
    """
    stream_ref = streams_collection.document(stream_id)
    stream_doc = stream_ref.get(transaction=transaction)

    if not stream_doc.exists:
        # This will cause the transaction to fail and roll back.
        raise HTTPException(status_code=404, detail="Stream not found")

    stream_data = stream_doc.to_dict()

    if not isinstance(drops, list):
        drops = [drops]

    added_drops = []
    prev_placement_id = stream_data.get('last_drop_placement_id')

    for drop_content in drops:
        # 1. Create the new drop
        drop_id = str(uuid.uuid4())
        new_drop = Drop(
            drop_id=drop_id,
            creator_id=creator_id,
            created_at=datetime.datetime.utcnow(),
            content=drop_content
        )
        drops_collection.document(drop_id).set(
            new_drop.dict()
        )

        # 2. Create the stream-drop placement
        placement_id = str(uuid.uuid4())

        new_placement = StreamDropPlacement(
            placement_id=placement_id,
            stream_id=stream_id,
            drop_id=drop_id,
            next_placement_id=None,
            prev_placement_id=prev_placement_id,
            added_at=datetime.datetime.utcnow()
        )
        stream_drops_collection.document(placement_id).set(
            new_placement.dict()
        )

        # 3. Update the previous placement's next_placement_id
        if prev_placement_id:
            prev_placement_ref = stream_drops_collection.document(
                prev_placement_id
            )
            transaction.update(
                prev_placement_ref, {'next_placement_id': placement_id}
            )

        # 4. Update the stream's head and tail pointers
        update_data = {'last_drop_placement_id': placement_id}
        if not stream_data.get('first_drop_placement_id'):
            update_data['first_drop_placement_id'] = placement_id
        
        transaction.update(stream_ref, update_data)

        # This data is returned after the transaction commits.
        added_drops.append(AddDropResponse(
            **new_drop.dict(),
            placement_id=placement_id,
            stream_id=stream_id,
            position_info={
                "next_placement_id": None,
                "prev_placement_id": prev_placement_id
            }
        ))
        prev_placement_id = placement_id
    
    return added_drops


@router.post(
    "/streams/{stream_id}/drops",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[AddDropResponse, AddDropsResponse]
)
def add_drop_to_stream(
    stream_id: str,
    drops: Union[DropContent, List[DropContent]],
    creator_id: str = Body(..., example="user_xyz")
):
    """
    Adds one or more drops to a stream. This is a transactional operation.
    """
    num_drops = len(drops) if isinstance(drops, list) else 1
    app_logger.info(
        f"Attempting to add {num_drops} drop(s) to stream {stream_id}"
    )
    try:
        @firestore.transactional
        def transactional_add(transaction):
            return _add_drops_transactional(
                transaction, stream_id, drops, creator_id
            )
        
        transaction = db.transaction()
        added_drops = transactional_add(transaction)

        if len(added_drops) == 1:
            app_logger.info(f"Successfully added 1 drop to stream {stream_id}")
            return added_drops[0]
        else:
            app_logger.info(
                f"Successfully added {len(added_drops)} drops to stream {stream_id}"
            )
            return AddDropsResponse(drops=added_drops)
    except Exception as e:
        # The transactional function raises an exception if the stream is not
        # found. We catch it and re-raise as a standard HTTPException.
        app_logger.error(
            f"Failed to add drop to stream {stream_id}: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/streams/{stream_id}/drops", response_model=GetDropsResponse)
def get_drops_in_stream(
    stream_id: str,
    from_placement_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get drops in a stream, with pagination.
    """
    app_logger.info(
        f"Attempting to get drops for stream {stream_id} with limit {limit}"
    )
    try:
        stream_doc = streams_collection.document(stream_id).get()
        if not stream_doc.exists:
            raise HTTPException(status_code=404, detail="Stream not found")

        stream_data = stream_doc.to_dict()
        
        if from_placement_id:
            start_at_doc = stream_drops_collection.document(
                from_placement_id
            ).get()
            if not start_at_doc.exists:
                raise HTTPException(
                    status_code=404, detail="Starting placement not found"
                )

            query = stream_drops_collection.where(
                'stream_id', '==', stream_id
            ).order_by('added_at').start_after(start_at_doc).limit(limit)
        else:
            # If no from_placement_id is provided, start from the beginning
            first_placement_id = stream_data.get('first_drop_placement_id')
            if not first_placement_id:
                # No drops in stream
                return GetDropsResponse(drops=[], has_more=False, total_count=0)

            start_at_doc = stream_drops_collection.document(
                first_placement_id
            ).get()
            query = stream_drops_collection.where(
                'stream_id', '==', stream_id
            ).order_by('added_at').start_at(start_at_doc).limit(limit)

        placements = query.stream()
        
        drops_list = []
        last_placement_doc = None
        for placement in placements:
            placement_data = placement.to_dict()
            drop_doc = drops_collection.document(
                placement_data['drop_id']
            ).get()
            if drop_doc.exists:
                drop_data = drop_doc.to_dict()
                
                # Combine drop data with placement data
                drop_in_stream = DropInStream(
                    **drop_data,
                    placement_id=placement_data['placement_id'],
                    next_placement_id=placement_data.get('next_placement_id'),
                    prev_placement_id=placement_data.get('prev_placement_id')
                )
                drops_list.append(drop_in_stream)
            last_placement_doc = placement

        # Check if there are more drops
        has_more = False
        if last_placement_doc:
            next_query = stream_drops_collection.where(
                'stream_id', '==', stream_id
            ).order_by('added_at').start_after(last_placement_doc).limit(1)
            if next(next_query.stream(), None):
                has_more = True

        # For total_count, we would ideally maintain a counter on the stream
        # document. For now, we'll do a full count, but this is not scalable.
        total_count_query = stream_drops_collection.where(
            'stream_id', '==', stream_id
        )
        total_count = len(list(total_count_query.stream()))
        
        app_logger.info(
            f"Successfully retrieved {len(drops_list)} drops for stream {stream_id}"
        )
        return GetDropsResponse(
            drops=drops_list, has_more=has_more, total_count=total_count
        )
    except Exception as e:
        app_logger.error(
            f"Failed to get drops for stream {stream_id}: {e}", exc_info=True
        )
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Failed to get drops.")
