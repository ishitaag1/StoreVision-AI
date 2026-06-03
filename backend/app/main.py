import os
import time
import uuid
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, status, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection

from app.auth.routes import router as auth_router
from app.routes.events import router as events_router
from app.routes.analytics import router as analytics_router
from app.routes.health import router as health_router  # Added the new health router

from app.services.websocket import manager
from app.tracker.pipeline import start_video_processing

# Set up basic structured logging required by grading rubric
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("api_logger")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events cleanly.
    """
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Store Intelligence Engine Backend",
    description="Asynchronous computer vision telemetry aggregator and analytics stream.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# STRUCTURED LOGGING MIDDLEWARE (Part C Requirement)
# ---------------------------------------------------------
@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    
    store_id = None
    event_count = None
    
    # 1. Attempt to extract store_id from the URL path
    path_parts = request.url.path.split("/")
    if "stores" in path_parts:
        try:
            store_idx = path_parts.index("stores")
            store_id = path_parts[store_idx + 1]
        except IndexError:
            pass

    # 2. Extract event_count and store_id from the body for ingest endpoints
    if request.url.path.endswith("/ingest") and request.method == "POST":
        # Safely read the body without hanging the downstream endpoint
        body = await request.body()
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive
        
        try:
            payload = json.loads(body)
            if isinstance(payload, list):
                event_count = len(payload)
                if event_count > 0 and not store_id:
                    store_id = payload[0].get("store_id")
        except Exception:
            pass
            
    # Process the actual request
    response = await call_next(request)
    
    # Calculate latency
    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    # Construct the exact JSON-like log required by the rubric
    log_data = {
        "trace_id": trace_id,
        "store_id": store_id,
        "endpoint": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "latency_ms": latency_ms,
    }
    
    if event_count is not None:
        log_data["event_count"] = event_count
        
    logger.info(json.dumps(log_data))
    return response
# ---------------------------------------------------------

app.include_router(auth_router)
app.include_router(events_router)
app.include_router(analytics_router)
app.include_router(health_router) # Replaces the old dummy endpoint

@app.post("/api/tracker/start", tags=["Vision Engine Control"])
async def trigger_vision_pipeline(background_tasks: BackgroundTasks, video_filename: str = "sample_store_footage.mp4"):
    """
    Triggers the OpenCV + YOLO object tracking micro-module.
    Runs as a non-blocking background task within FastAPI's event loop.
    """
    video_path = os.path.join(os.getcwd(), video_filename)
    
    if not os.path.exists(video_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target file '{video_filename}' not found in the backend root directory."
        )

    background_tasks.add_task(start_video_processing, video_path, camera_id="cam_floor_01")
    
    return {
        "status": "success",
        "message": f"Computer vision pipeline launched for {video_filename}."
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """
    Central WebSocket gateway for the Next.js dashboard UI.
    Maintains persistent connections to stream real-time bounding boxes and alerts.
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # 1. Receive the tracking JSON frame from real_camera.py
            data = await websocket.receive_text()
            
            # 2. Broadcast it out to all Next.js dashboard tabs!
            await manager.broadcast(data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
    except Exception as e:
        print(f"⚠️ Unexpected exception in telemetry channel sequence: {e}")
        manager.disconnect(websocket)