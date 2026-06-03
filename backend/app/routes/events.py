from fastapi import APIRouter, HTTPException, Query, status, Depends
from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import get_collection
from app.auth.dependencies import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/api/events", tags=["Event Logs Engine"])

# ==========================================
# 📋 PYDANTIC DATA MODELS & SCHEMA COMPLIANCE [cite: 63, 171]
# ==========================================

class EventMetadata(BaseModel):
    queue_depth: Optional[int] = Field(default=None, description="Current depth size if channel matches BILLING_QUEUE_JOIN")

class StoreEventModel(BaseModel):
    event_id: str = Field(..., description="Globally unique UUID-v4 transaction string identifier")
    store_id: str = Field(..., description="Unique alphanumeric location code footprint key")
    camera_id: str = Field(..., description="Source camera asset code identifier tracker")
    visitor_id: str = Field(..., description="Persistent Re-ID tracking session token sequence string")
    event_type: str = Field(..., description="Action category flag (ENTRY, EXIT, ZONE_ENTER, ZONE_EXIT, etc.)")
    timestamp: datetime = Field(..., description="ISO-8601 UTC timestamp profile index wrapper")
    zone_id: Optional[str] = Field(default=None, description="Monitored specific location layout area tag")
    dwell_ms: int = Field(default=0, ge=0, description="Continuous residence delta inside zone coordinates")
    is_staff: bool = Field(default=False, description="Flag indicating if the target sequence correlates to active staff")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Raw confidence score output matrix value")
    metadata: EventMetadata = Field(default_factory=EventMetadata, description="Extensible object payload parameters container")

class IngestResponseSummary(BaseModel):
    status: str
    processed: int
    duplicates: int
    failed: int
    errors: List[Dict[str, Any]]

# ==========================================
# 🔘 POST /api/events/ingest ROUTE HANDLER 
# ==========================================

@router.post("/ingest", response_model=IngestResponseSummary, status_code=status.HTTP_201_CREATED)
async def ingest_store_events_batch(
    payload: List[Dict[str, Any]], 
):
    """
    Ingests and processes batches of up to 500 store events.
    Enforces strict idempotency constraints and supports partial success patterns.
    """
    # 1. Enforce batch item constraints 
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch payload density limitation exceeded. Maximum capacity constraint is 500 items per array slice."
        )

    events_collection = get_collection("events")
    
    processed_count = 0
    duplicate_count = 0
    failed_count = 0
    error_logs: List[Dict[str, Any]] = []
    
    # Pre-extract existing event IDs in this batch to enforce idempotency in a single query 
    provided_ids = [str(item.get("event_id")) for item in payload if item.get("event_id")]
    existing_records = await events_collection.find({"event_id": {"$in": provided_ids}}).to_list(length=len(provided_ids))
    existing_ids = {doc["event_id"] for doc in existing_records}

    for index, raw_item in enumerate(payload):
        try:
            # 2. Scheme Compliance Verification via Pydantic [cite: 93]
            validated_event = StoreEventModel(**raw_item)
            
            # 3. Idempotency Guard 
            if validated_event.event_id in existing_ids:
                duplicate_count += 1
                continue
                
            # Convert validated Pydantic object structure to a MongoDB BSON compatible dictionary payload
            document = validated_event.model_dump()
            
            # Persist datetime fields cleanly as native BSON dates rather than strings
            document["timestamp"] = validated_event.timestamp
            
            # Write document execution record to MongoDB database collection
            await events_collection.insert_one(document)
            processed_count += 1
            
        except Exception as validation_error:
            # 4. Partial Success Path Engine Configuration 
            failed_count += 1
            error_logs.append({
                "batch_index": index,
                "provided_event_id": raw_item.get("event_id", "MISSING"),
                "error_nature": str(validation_error)
            })

    # Determine structured success state profile response flags 
    status_flag = "success" if failed_count == 0 else "partial_success"
    
    return IngestResponseSummary(
        status=status_flag,
        processed=processed_count,
        duplicates=duplicate_count,
        failed=failed_count,
        errors=error_logs
    )

# ==========================================
# 🔍 GET LOOKUP ROUTES (Preserved from original code architecture)
# ==========================================

@router.get("/", response_description="List paginated events matching search queries")
async def get_historical_events(
    camera_id: Optional[str] = Query(None, description="Filter logs by a specific camera identifier"),
    event_type: Optional[str] = Query(None, description="Filter logs by type (e.g., person_tracking, anomaly)"),
    start_time: Optional[datetime] = Query(None, description="Query frame start marker (ISO Format)"),
    end_time: Optional[datetime] = Query(None, description="Query frame close window (ISO Format)"),
    page: int = Query(1, ge=1, description="Current list pagination sequence number"),
    limit: int = Query(50, le=100, description="Maximum database records to fetch per sequence shift"),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieves filtered logs from the MongoDB events collection for data tables.
    """
    events_collection = get_collection("events")
    
    query = {}
    if camera_id:
        query["camera_id"] = camera_id
    if event_type:
        query["event_type"] = event_type
        
    if start_time or end_time:
        query["timestamp"] = {}
        if start_time:
            query["timestamp"]["$gte"] = start_time
        if end_time:
            query["timestamp"]["$lte"] = end_time

    skip = (page - 1) * limit

    cursor = events_collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    
    events = []
    async for document in cursor:
        document["id"] = str(document["_id"])
        del document["_id"]
        events.append(document)

    total_records = await events_collection.count_documents(query)

    return {
        "status": "success",
        "meta": {
            "total_records": total_records,
            "page": page,
            "limit": limit,
            "total_pages": (total_records + limit - 1) // limit
        },
        "data": events
    }

@router.get("/{event_id}", response_description="Fetch explicit object tracking attributes")
async def get_event_by_id(event_id: str, current_user: dict = Depends(get_current_user)):
    """
    Fetches the full JSON payload of a single event using its unique MongoDB Hex string ID.
    """
    if not ObjectId.is_valid(event_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid event format signature.")
        
    events_collection = get_collection("events")
    event = await events_collection.find_one({"_id": ObjectId(event_id)})
    
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target tracking event registry not found.")
        
    event["id"] = str(event["_id"])
    del event["_id"]
    return {"status": "success", "data": event}