# Engineering Choices & AI Utilization

## 1. Detection Model Selection
* **Options Considered:** Faster R-CNN, MediaPipe, YOLOv8n.
* **What AI Suggested:** The LLM suggested YOLOv8n (Nano) paired with ByteTrack, noting that it provides the best trade-off between inference speed and accuracy for edge devices without dedicated GPUs.
* **What I Chose & Why:** I chose **YOLOv8n**. In a retail environment, high FPS throughput is crucial to accurately track fast-moving customers across camera overlaps. Faster R-CNN was too computationally expensive, and MediaPipe struggled with multi-person occlusion in the billing queue. I supplemented YOLOv8 with a custom heuristics pipeline (checking for black staff uniforms via NumPy masking) rather than deploying a heavy VLM, as it kept the edge footprint minimal and latency low.

## 2. Event Schema Design Rationale
* **Options Considered:** Highly normalized relational SQL tables vs. Flat NoSQL JSON documents.
* **What AI Suggested:** The AI recommended a NoSQL document structure with a flexible `metadata` payload to easily accommodate different event types without schema migrations.
* **What I Chose & Why:** I chose the **Flat JSON NoSQL** approach using MongoDB. Because telemetry streams emit thousands of heterogeneous events (an `ENTRY` event doesn't need a `queue_depth` field, but a `BILLING` event does), forcing this into a rigid SQL table would result in too many sparse columns. The `metadata` object allows dynamic data injection while keeping the root schema standard and strictly validated by Pydantic.

## 3. API Architecture Choice
* **Options Considered:** Express.js (Node), Django (Python), FastAPI (Python).
* **What AI Suggested:** The AI heavily favored FastAPI due to its native asynchronous support (`asyncio`) and out-of-the-box Pydantic integration for data validation.
* **What I Chose & Why:** I chose **FastAPI**. The telemetry ingest route (`/events/ingest`) receives massive bursts of concurrent batch requests. FastAPI handles asynchronous I/O exceptionally well, preventing network bottlenecks. Furthermore, FastAPI's built-in WebSockets made streaming the live tracking bounding boxes to the Next.js frontend significantly easier than configuring Socket.io on a separate Node.js server.