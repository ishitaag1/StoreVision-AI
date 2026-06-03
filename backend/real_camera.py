# import cv2
# import json
# import asyncio
# import websockets
# from datetime import datetime, timezone
# from ultralytics import YOLO

# WS_URL = "ws://127.0.0.1:8000/ws/telemetry"

# async def stream_real_camera():
#     print("🚀 Loading YOLOv8 Model...")

#     model = YOLO("app/tracker/weights/yolov8n.pt")
    
#     cap = cv2.VideoCapture(0)
    
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#     print(f"🎥 Connecting to StoreIntel Engine at {WS_URL}...")
    
#     try:
#         async with websockets.connect(WS_URL, ping_interval=None) as websocket:
#             print("✅ Successfully connected! Starting real-time AI inference...")
            
#             current_id = 1

#             while cap.isOpened():
#                 success, frame = cap.read()
#                 if not success:
#                     print("❌ Failed to grab frame from webcam.")
#                     break

#                 results = model(frame, classes=[0], verbose=False)

#                 for r in results:
#                     boxes = r.boxes
#                     for box in boxes:
#                         x1, y1, x2, y2 = box.xyxy[0].tolist()
#                         conf = float(box.conf[0])

#                         telemetry_payload = {
#                             "stream_type": "live_telemetry",
#                             "data": {
#                                 "camera_id": "webcam_01",
#                                 "timestamp": datetime.now(timezone.utc).isoformat(),
#                                 "event_type": "person_tracking",
#                                 "entity_id": current_id, 
#                                 "confidence": round(conf, 2),
#                                 "box": {
#                                     "x1": x1,
#                                     "y1": y1,
#                                     "x2": x2,
#                                     "y2": y2
#                                 },
#                                 "metadata": {"zone": "Live Webcam"}
#                             }
#                         }
                        
#                         await websocket.send(json.dumps(telemetry_payload))
                        
#                         current_id = (current_id % 100) + 1 

#                 cv2.imshow("StoreIntel Raw AI Feed", frame)
#                 if cv2.waitKey(1) & 0xFF == ord("q"):
#                     break
                
#                 await asyncio.sleep(0.1) 

#     except ConnectionRefusedError:
#         print("❌ Connection Refused. Is your FastAPI backend running on port 8000?")
#     except Exception as e:
#         print(f"❌ Connection lost: {e}")
#     finally:
#         cap.release()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     try:
#         asyncio.run(stream_real_camera())
#     except KeyboardInterrupt:
#         print("\n🛑 Camera stream stopped cleanly by user.")

import cv2
import json
import asyncio
import websockets
from datetime import datetime, timezone
from ultralytics import YOLO

WS_URL = "ws://127.0.0.1:8000/ws/telemetry"

async def stream_real_camera():
    print("🚀 Loading YOLOv8 Model...")
    model = YOLO("app/tracker/weights/yolov8n.pt")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print(f"🎥 Connecting to StoreIntel Engine at {WS_URL}...")
    
    try:
        async with websockets.connect(WS_URL, ping_interval=None) as websocket:
            print("✅ Successfully connected! Starting real-time AI inference...")
            current_id = 1

            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    print("❌ Failed to grab frame from webcam.")
                    break

                # 🔥 FIX: Run the heavy YOLO model inside a separate background thread!
                # This stops the AI from blocking our network heartbeats.
                results = await asyncio.to_thread(model, frame, classes=[0], verbose=False)

                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        conf = float(box.conf[0])

                        telemetry_payload = {
                            "stream_type": "live_telemetry",
                            "data": {
                                "camera_id": "webcam_01",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "event_type": "person_tracking",
                                "entity_id": current_id, 
                                "confidence": round(conf, 2),
                                "box": {
                                    "x1": x1,
                                    "y1": y1,
                                    "x2": x2,
                                    "y2": y2
                                },
                                "metadata": {"zone": "Live Webcam"}
                            }
                        }
                        await websocket.send(json.dumps(telemetry_payload))
                        current_id = (current_id % 100) + 1 

                # Optional: Comment this line out with a '#' if you want to close the popup window
                cv2.imshow("StoreIntel Raw AI Feed", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                
                await asyncio.sleep(0.1) 

    except ConnectionRefusedError:
        print("❌ Connection Refused. Is your FastAPI backend running on port 8000?")
    except Exception as e:
        print(f"❌ Connection lost: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        asyncio.run(stream_real_camera())
    except KeyboardInterrupt:
        print("\n🛑 Camera stream stopped cleanly by user.")