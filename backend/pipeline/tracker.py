# pipeline/tracker.py
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional

# Layout Zone Mappings matching the 'Store 1 - layout.jpg' specifications
# Normalized coordinates mapped across a standard 1080p surveillance video frame
STORE_LAYOUT_POLYGONS = {
    "CAM_FLOOR_01": {
        "MINIMALIS": np.array([(100, 100), (450, 100), (450, 400), (100, 400)], dtype=np.int32),
        "AQUALOGI": np.array([(500, 100), (850, 100), (850, 400), (500, 400)], dtype=np.int32),
        "LOREAL": np.array([(100, 700), (450, 700), (450, 1050), (100, 1050)], dtype=np.int32),
        "BEAUT": np.array([(500, 700), (850, 700), (850, 1050), (500, 1050)], dtype=np.int32),
    },
    "CAM_BILLING_01": {
        "PURPLLE_MUM_1076_Z_BILLING_01": np.array([(200, 200), (900, 200), (900, 950), (200, 950)], dtype=np.int32)
    }
}

# ✅ FIXED: Harmonized variable name to match usage inside functions perfectly
ENTRY_THRESHOLD_Y_LINE = 600  

class SpatialStateTracker:
    def __init__(self):
        self.trajectory_history: Dict[int, List[Tuple[int, int]]] = {}
        self.active_zone_dwells: Dict[Tuple[int, str], datetime] = {}
        self.last_dwell_emission: Dict[Tuple[int, str], datetime] = {}
        self.billing_queue_registry: Set[int] = set()
        self.historical_exit_registry: Dict[str, datetime] = {}  # visitor_token -> exit_time

    def evaluate_staff_uniform_ratio(self, frame, bbox: List[float]) -> bool:
        """
        Analyzes HSV color histograms within item crops to classify employees.
        """
        x1, y1, x2, y2 = map(int, bbox)
        crop = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
        if crop.size == 0:
            return False
        hsv_image = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        # Uniform profile boundaries matching standard corporate black attributes
        lower_bound = np.array([0, 0, 0])
        upper_bound = np.array([180, 255, 40])
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        ratio = np.sum(mask > 0) / crop.size
        
        # ✅ FIXED: Explicitly wrap with bool() to cast numpy.bool_ to a native Python serializable bool
        return bool(ratio > 0.50)  

    def process_spatial_rules(self, track_id: int, bbox: List[float], camera_id: str, current_time: datetime, frame) -> List[Tuple[str, Dict]]:
        """
        Calculates bottom-center centroids and returns parsed event types.
        """
        x1, y1, x2, y2 = bbox
        cx = int(x1 + (x2 - x1) / 2)
        cy = int(y2)  # Base boundary center point
        
        visitor_token = str(track_id)
        is_staff = self.evaluate_staff_uniform_ratio(frame, bbox)
        generated_events = []

        if track_id not in self.trajectory_history:
            self.trajectory_history[track_id] = []
        self.trajectory_history[track_id].append((cx, cy))

        # ----------------------------------------------------------------------
        # BOUNDARY VECTOR 1: ENTRY/EXIT THRESHOLD INTERSECT CALCULATIONS
        # ----------------------------------------------------------------------
        if camera_id == "CAM_ENTRY_01" and len(self.trajectory_history[track_id]) >= 2:
            past_cy = self.trajectory_history[track_id][-2][1]
            
            # Crosses down (Inbound)
            if past_cy < ENTRY_THRESHOLD_Y_LINE <= cy:
                if visitor_token in self.historical_exit_registry:
                    generated_events.append(("REENTRY", {"zone_id": None, "dwell_ms": 0, "is_staff": is_staff, "queue_depth": None}))
                else:
                    generated_events.append(("ENTRY", {"zone_id": None, "dwell_ms": 0, "is_staff": is_staff, "queue_depth": None}))
            
            # Crosses up (Outbound)
            elif past_cy >= ENTRY_THRESHOLD_Y_LINE > cy:
                generated_events.append(("EXIT", {"zone_id": None, "dwell_ms": 0, "is_staff": is_staff, "queue_depth": None}))
                self.historical_exit_registry[visitor_token] = current_time

        # ----------------------------------------------------------------------
        # BOUNDARY VECTOR 2: SPATIAL POLYGON LAYOUT DETECTION
        # ----------------------------------------------------------------------
        active_camera_polygons = STORE_LAYOUT_POLYGONS.get(camera_id, {})
        is_inside_any_zone = False

        for zone_id, polygon_array in active_camera_polygons.items():
            # Run the deterministic geometric inside-outside test routine
            coordinate_check = cv2.pointPolygonTest(polygon_array, (cx, cy), False)
            
            if coordinate_check >= 0:
                is_inside_any_zone = True
                state_key = (track_id, zone_id)

                if state_key not in self.active_zone_dwells:
                    self.active_zone_dwells[state_key] = current_time
                    self.last_dwell_emission[state_key] = current_time
                    generated_events.append(("ZONE_ENTER", {"zone_id": zone_id, "dwell_ms": 0, "is_staff": is_staff, "queue_depth": None}))

                    if "BILLING" in zone_id and not is_staff:
                        current_depth = len(self.billing_queue_registry)
                        self.billing_queue_registry.add(track_id)
                        generated_events.append(("BILLING_QUEUE_JOIN", {"zone_id": zone_id, "dwell_ms": 0, "is_staff": is_staff, "queue_depth": current_depth}))
                else:
                    entry_start = self.active_zone_dwells[state_key]
                    previous_emit = self.last_dwell_emission[state_key]
                    
                    total_dwell_duration = (current_time - entry_start).total_seconds()
                    seconds_since_last_emit = (current_time - previous_emit).total_seconds()

                    # Emit consecutive DWELL events every 30 seconds
                    if seconds_since_last_emit >= 30.0:
                        generated_events.append(("ZONE_DWELL", {"zone_id": zone_id, "dwell_ms": total_dwell_duration * 1000, "is_staff": is_staff, "queue_depth": None}))
                        self.last_dwell_emission[state_key] = current_time

        # Handle zone exit checks
        exit_keys_to_purge = []
        for state_key, entry_start in self.active_zone_dwells.items():
            t_id, z_id = state_key
            if t_id == track_id and not is_inside_any_zone:
                accumulated_ms = (current_time - entry_start).total_seconds() * 1000
                generated_events.append(("ZONE_EXIT", {"zone_id": z_id, "dwell_ms": accumulated_ms, "is_staff": is_staff, "queue_depth": None}))
                if t_id in self.billing_queue_registry:
                    self.billing_queue_registry.discard(t_id)
                exit_keys_to_purge.append(state_key)

        for key in exit_keys_to_purge:
            self.active_zone_dwells.pop(key, None)
            self.last_dwell_emission.pop(key, None)

        return generated_events