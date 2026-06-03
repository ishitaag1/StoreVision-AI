# pipeline/emit.py
import requests
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

INGEST_URL = "http://127.0.0.1:8000/api/events/ingest"

class EventEmitter:
    def __init__(self, batch_size: int = 100):
        self.batch_size = min(batch_size, 500)  # Capped at problem statement constraint limits
        self.event_queue: List[Dict[str, Any]] = []
        print(f"📡 Event Emitter initialized. Batch transaction window: {self.batch_size} events.")

    def format_event(
        self,
        store_id: str,
        camera_id: str,
        visitor_id: str,
        event_type: str,
        timestamp: datetime,
        confidence: float,
        zone_id: Optional[str] = None,
        dwell_ms: int = 0,
        is_staff: bool = False,
        queue_depth: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Structures transaction inputs to guarantee strict compatibility with the Pydantic ingestion schema.
        """
        return {
            "event_id": str(uuid.uuid4()),  # Generates globally unique UUID-v4 token keys
            "store_id": store_id,
            "camera_id": camera_id,
            "visitor_id": f"VIS_{visitor_id}",
            "event_type": event_type,
            "timestamp": timestamp.isoformat().replace("+00:00", "Z"),  # Enforces ISO-8601 string formatting
            "zone_id": zone_id,
            "dwell_ms": int(dwell_ms),
            "is_staff": is_staff,
            "confidence": round(float(confidence), 2),
            "metadata": {
                "queue_depth": queue_depth
            }
        }

    def emit(self, event_payload: Dict[str, Any]):
        """
        Appends single payload records into a memory buffer and checks threshold execution windows.
        """
        self.event_queue.append(event_payload)
        if len(self.event_queue) >= self.batch_size:
            self.flush()

    def flush(self):
        """
        Transfers memory buffer arrays via an HTTP POST request to the server database gateway.
        """
        if not self.event_queue:
            return

        batch_to_ship = list(self.event_queue)
        self.event_queue.clear()

        print(f"📤 Blasting payload batch package containing ({len(batch_to_ship)}) elements to database gateway...")
        try:
            # Connect directly to the authenticated database batch endpoint
            response = requests.post(INGEST_URL, json=batch_to_ship, timeout=10)
            if response.status_code in [200, 201]:
                summary = response.json()
                print(f"✅ Batch processed successfully: {summary.get('processed', 0)} logged, {summary.get('duplicates', 0)} skipped.")
            else:
                print(f"⚠️ Batch rejected with code ({response.status_code}): {response.text}")
        except requests.exceptions.RequestException as network_error:
            print(f"❌ Failed to reach web server API pipeline context layer: {network_error}")