from fastapi import APIRouter, HTTPException, status, Body, Query
from app.models import (
    Stream,
    StreamContent,
    Drop,
    DropContent,
    StreamDropPlacement,
    AddDropResponse,
    GetDropsResponse,
    DropInStream,
    AddDropsResponse,
    StreamListResponse,
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


@router.get(
    "/pools/{pool_id}/streams",
    response_model=StreamListResponse,
)
def list_streams_in_pool(
    pool_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    creator_id: Optional[str] = Query(None),
):
    """Returns paginated streams inside a pool."""

    app_logger.info(
        "Listing streams for pool %s with limit=%s offset=%s creator_id=%s",
        pool_id,
        limit,
        offset,
        creator_id,
    )

    try:
        pool_doc = pools_collection.document(pool_id).get()
        if not pool_doc.exists:
            raise HTTPException(status_code=404, detail="Pool not found")

        query = streams_collection.where("pool_id", "==", pool_id)
        if creator_id:
            query = query.where("creator_id", "==", creator_id)

        total_count = len(list(query.stream()))

        ordered_query = query.order_by("created_at")
        if offset:
            ordered_query = ordered_query.offset(offset)

        stream_docs = ordered_query.limit(limit).stream()
        streams = [Stream(**doc.to_dict()) for doc in stream_docs]

        next_offset = offset + len(streams)
        has_more = next_offset < total_count

        return StreamListResponse(
            streams=streams,
            total_count=total_count,
            has_more=has_more,
            next_offset=next_offset if has_more else None,
        )
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(
            "Failed listing streams for pool %s: %s", pool_id, e, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to list streams.")


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
        app_logger.info(
            "Successfully created stream %s in pool %s",
            stream_id,
            pool_id,
        )
        return new_stream
    except Exception as e:
        app_logger.error(
            "Failed to create stream in pool %s: %s",
            pool_id,
            e,
            exc_info=True,
        )
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
        app_logger.error(
            "Failed to retrieve stream %s: %s",
            stream_id,
            e,
            exc_info=True,
        )
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve stream.",
        )


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

    first_pointer_set = bool(stream_data.get('first_drop_placement_id'))

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
        if not first_pointer_set:
            update_data['first_drop_placement_id'] = placement_id
            first_pointer_set = True
            stream_data['first_drop_placement_id'] = placement_id
        
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
                "Successfully added %s drops to stream %s",
                len(added_drops),
                stream_id,
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
    limit: int = Query(10, ge=-50, le=50)
):
    """
    Get drops in a stream using linked list traversal.
    Positive limit: forward traversal (using next_placement_id).
    Negative limit: backward traversal (using prev_placement_id).
    """
    if limit == 0:
        raise HTTPException(
            status_code=422, detail="Limit cannot be zero"
        )
    
    app_logger.info(
        f"Attempting to get drops for stream {stream_id} with limit {limit}"
    )
    
    is_forward = limit > 0
    actual_limit = abs(limit)
    
    try:
        stream_doc = streams_collection.document(stream_id).get()
        if not stream_doc.exists:
            raise HTTPException(status_code=404, detail="Stream not found")

        stream_data = stream_doc.to_dict()
        
        # Determine starting placement
        if from_placement_id:
            current_placement_id = from_placement_id
        else:
            # No starting point specified
            if is_forward:
                current_placement_id = stream_data.get('first_drop_placement_id')
            else:
                current_placement_id = stream_data.get('last_drop_placement_id')
        
        if not current_placement_id:
            # No drops in stream
            return GetDropsResponse(
                drops=[],
                has_more=False,
                total_count=0,
            )
        
        # Traverse the linked list
        drops_list = []
        visited_count = 0
        
        while current_placement_id and visited_count < actual_limit:
            # Get the placement
            placement_doc = stream_drops_collection.document(
                current_placement_id
            ).get()
            
            if not placement_doc.exists:
                app_logger.warning(
                    f"Placement {current_placement_id} not found in stream {stream_id}"
                )
                break
            
            placement_data = placement_doc.to_dict()
            
            # Verify this placement belongs to the stream
            if placement_data.get('stream_id') != stream_id:
                app_logger.error(
                    f"Placement {current_placement_id} does not belong to stream {stream_id}"
                )
                break
            
            # Get the drop
            drop_doc = drops_collection.document(
                placement_data['drop_id']
            ).get()
            
            if drop_doc.exists:
                drop_data = drop_doc.to_dict()
                
                drop_in_stream = DropInStream(
                    **drop_data,
                    placement_id=placement_data['placement_id'],
                    next_placement_id=placement_data.get('next_placement_id'),
                    prev_placement_id=placement_data.get('prev_placement_id')
                )
                drops_list.append(drop_in_stream)
                visited_count += 1
            
            # Move to next placement
            if is_forward:
                current_placement_id = placement_data.get('next_placement_id')
            else:
                current_placement_id = placement_data.get('prev_placement_id')
        
        # Check if there are more drops
        has_more = current_placement_id is not None
        
        # For total_count, we would ideally maintain a counter on the stream
        # document. For now, we'll do a full count, but this is not scalable.
        total_count_query = stream_drops_collection.where(
            'stream_id', '==', stream_id
        )
        total_count = len(list(total_count_query.stream()))
        
        app_logger.info(
            "Successfully retrieved %s drops for stream %s using linked list",
            len(drops_list),
            stream_id,
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
