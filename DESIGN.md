# Store Intelligence System - Architecture Design
**Author:** Sankalpa Panda

## System Overview
The Store Intelligence System is an end-to-end computer vision and business analytics pipeline designed to monitor physical retail spaces. It tracks customer foot traffic, calculates zone dwell times, and derives business metrics (like Conversion Rate and Funnel Drop-off) by correlating spatial data with Point-of-Sale (POS) transactions.

## Architecture Data Flow
The system is built on a microservices-inspired architecture comprising three main layers:

1. **The Edge Vision Pipeline (Python/YOLOv8)**
   * **Ingestion:** Reads RTSP/MP4 video files frame-by-frame.
   * **Inference:** Utilizes YOLOv8n (Nano) for high-speed person detection, paired with ByteTrack for persistent ID tracking across frames.
   * **Spatial Math:** Calculates bottom-center bounding box coordinates to determine if a customer crosses the entry threshold or dwells within defined geometric product zones.
   * **Batch Emitter:** Buffers tracking events locally and blasts them to the backend in batches of 50 to prevent network bottlenecking.

2. **The Core API Server (FastAPI)**
   * **REST Ingestion:** Receives batch payloads, validates schemas using Pydantic, checks for idempotency, and persists them to MongoDB.
   * **Business Logic:** Correlates spatial exit events with POS CSV transaction timestamps (using a 5-minute window) to calculate the Store Conversion Rate.
   * **Live Telemetry:** Maintains an active WebSocket connection to broadcast live bounding box coordinates and critical security anomalies.

3. **The Presentation Layer (Next.js/React)**
   * **Live Matrix:** Consumes the WebSocket feed to draw real-time tracking boxes on an HTML5 Canvas.
   * **Business Dashboard:** Fetches aggregated metrics via Axios and visualizes zone densities and funnel drop-offs using Recharts.

## Database Schema (MongoDB)
We utilize a flexible NoSQL document structure. A standard event document follows this schema:
```json
{
  "event_id": "uuid-v4",
  "store_id": "STORE_BLR_002",
  "camera_id": "CAM_ENTRY_01",
  "visitor_id": "14",
  "event_type": "ZONE_DWELL",
  "timestamp": "2026-04-10T14:15:30Z",
  "metadata": {
    "zone_id": "LOREAL",
    "dwell_ms": 45000,
    "is_staff": false
  }
}