# backend/app/routes/health.py
from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
from app.database import get_collection

router = APIRouter()

@router.get("/health", tags=["System Diagnostics"])
async def health_check():
    """
    Verifies API gateway status and monitors CCTV feed recency.
    Returns STALE_FEED if no events received in the last 10 minutes.
    """
    events_col = get_collection("events")
    
    # Fetch the most recent event to check the feed status
    latest_event = await events_col.find_one(sort=[("timestamp", -1)])
    
    status = "healthy"
    warnings = []
    last_event_time = None
    
    if latest_event and "timestamp" in latest_event:
        try:
            # Parse the ISO timestamp correctly
            event_dt = datetime.fromisoformat(latest_event["timestamp"].replace("Z", "+00:00"))
            last_event_time = latest_event["timestamp"]
            
            # Check if the feed is lagging by more than 10 minutes
            if datetime.now(timezone.utc) - event_dt > timedelta(minutes=10):
                warnings.append("STALE_FEED")
                status = "degraded"
        except Exception as e:
            warnings.append(f"Timestamp parsing error: {str(e)}")

    return {
        "service": "store-intelligence-api",
        "status": status,
        "warnings": warnings,
        "last_event_timestamp": last_event_time
    }