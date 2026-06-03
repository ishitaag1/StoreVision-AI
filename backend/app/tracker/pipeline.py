import cv2
import asyncio
from datetime import datetime
from ultralytics import YOLO
from app.database import get_collection
from app.services.websocket import manager
from app.services.anomaly import analyze_event_for_anomalies, clear_cached_entity

async def start_video_processing(video_path: str, camera_id: str = "cam_floor_01"):
    """
    Asynchronous Computer Vision Pipeline.
    Loads the local YOLO weights, processes video frame-by-frame,
    saves tracking footprints to MongoDB, runs anomaly checks, and
    streams data live to the frontend dashboard.
    """
    try:
        model = YOLO("app/tracker/weights/yolov8n.pt")
    except Exception as e:
        print(f"❌ Error loading YOLO model weights: {e}")
        print("Please ensure 'yolov8n.pt' is downloaded inside 'app/tracker/weights/'")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error: Could not open video source at {video_path}")
        return

    events_collection = get_collection("events")
    
    print(f"🎬 Local vision pipeline started for {camera_id}...")

    prev_active_ids = set()

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("🏁 Video stream reached the end or disconnected.")
                break

            results = model.track(frame, persist=True, classes=[0], verbose=False)

            current_active_ids = set()

            if results[0].boxes and results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                confidences = results[0].boxes.conf.cpu().numpy()

                for box, track_id, confidence in zip(boxes, track_ids, confidences):
                    current_active_ids.add(track_id)
                    x1, y1, x2, y2 = map(float, box)

                    event_payload = {
                        "camera_id": camera_id,
                        "timestamp": datetime.utcnow(),
                        "event_type": "person_tracking",
                        "entity_id": track_id,
                        "confidence": round(float(confidence), 2),
                        "box": {
                            "x1": round(x1, 1),
                            "y1": round(y1, 1),
                            "x2": round(x2, 1),
                            "y2": round(y2, 1)
                        },
                        "metadata": {
                            "zone": "restricted_warehouse_door" if x1 < 300 else "main_checkout_aisle"
                        }
                    }

                    await events_collection.insert_one(event_payload.copy())

                    anomaly_alert = await analyze_event_for_anomalies(event_payload)
                    if anomaly_alert:
                        await manager.broadcast({
                            "stream_type": "security_alert",
                            "data": anomaly_alert
                        })

                    await manager.broadcast({
                        "stream_type": "live_telemetry",
                        "data": {
                            **event_payload,
                            "timestamp": event_payload["timestamp"].isoformat() + "Z"
                        }
                    })

            expired_ids = prev_active_ids - current_active_ids
            for old_id in expired_ids:
                clear_cached_entity(old_id)
            prev_active_ids = current_active_ids

            await asyncio.sleep(0.01)

    except asyncio.CancelledError:
        print("🛑 Vision pipeline background execution terminated intentionally.")
    finally:
        cap.release()
        print(f"🔌 Visual stream processing resources released for {camera_id}.")