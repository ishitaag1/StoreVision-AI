from datetime import datetime
from app.database import get_collection

ZONE_TRACKER = {}

LOITERING_THRESHOLD_SECONDS = 15.0

async def analyze_event_for_anomalies(event_data: dict) -> dict | None:
    """
    Parses tracking telemetry frames dynamically to catch behavioral anomalies.
    
    Args:
        event_data (dict): The unpacked event object written by the YOLO vision pipeline.
        
    Returns:
        dict | None: Returns an anomaly event payload if a rule threshold is violated.
    """
    entity_id = event_data.get("entity_id")
    event_type = event_data.get("event_type")
    metadata = event_data.get("metadata", {})
    zone = metadata.get("zone", "unknown")
    
    if event_type != "person_tracking" or entity_id is None:
        return None

    current_time = datetime.utcnow()

    if entity_id not in ZONE_TRACKER:
        ZONE_TRACKER[entity_id] = {"zone": zone, "entered_at": current_time, "alert_triggered": False}
    
    tracked_entity = ZONE_TRACKER[entity_id]

    if tracked_entity["zone"] != zone:
        tracked_entity["zone"] = zone
        tracked_entity["entered_at"] = current_time
        tracked_entity["alert_triggered"] = False

    dwell_time = (current_time - tracked_entity["entered_at"]).total_seconds()
    
    if zone in ["restricted_warehouse_door", "back_alley_exit"] and dwell_time > LOITERING_THRESHOLD_SECONDS:
        if not tracked_entity["alert_triggered"]:
            tracked_entity["alert_triggered"] = True
            
            anomaly_payload = {
                "camera_id": event_data.get("camera_id"),
                "timestamp": current_time,
                "event_type": "anomaly_loitering",
                "entity_id": entity_id,
                "confidence": event_data.get("confidence", 1.0),
                "box": event_data.get("box"),
                "metadata": {
                    "zone": zone,
                    "duration_seconds": round(dwell_time, 1),
                    "alert_level": "high",
                    "description": f"Entity #{entity_id} has been loitering in restricted zone '{zone}' for over {LOITERING_THRESHOLD_SECONDS}s."
                }
            }
            
            anomalies_collection = get_collection("anomalies")
            await anomalies_collection.insert_one(anomaly_payload.copy())
            
            return anomaly_payload

    return None

def clear_cached_entity(entity_id: int):
    """ Cleans up memory cache once an entity leaves the camera frame entirely. """
    if entity_id in ZONE_TRACKER:
        del ZONE_TRACKER[entity_id]