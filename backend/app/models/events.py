from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class BoundingBox(BaseModel):
    """
    Coordinates representing a spatial boundary around a tracked object.
    """
    x1: float = Field(..., description="Top-left corner X pixel value")
    y1: float = Field(..., description="Top-left corner Y pixel value")
    x2: float = Field(..., description="Bottom-right corner X pixel value")
    y2: float = Field(..., description="Bottom-right corner Y pixel value")

class StoreEventModel(BaseModel):
    """
    The formal structural layout for computer vision analytics and system logs.
    """
    camera_id: str = Field(..., description="Identifier mapping back to physical hardware location")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC event recording time")
    event_type: str = Field(..., description="Functional tag (e.g., person_tracking, crowd_density, anomaly)")
    entity_id: Optional[int] = Field(None, description="Persistent tracker ID assigned across video frames")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection algorithm statistical precision metric")
    box: Optional[BoundingBox] = Field(None, description="Spatial boundaries; missing if event represents structural logic")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extensible contextual tracking parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "camera_id": "cam_aisle_02",
                "timestamp": "2026-06-01T12:00:00Z",
                "event_type": "person_tracking",
                "entity_id": 45,
                "confidence": 0.94,
                "box": {
                    "x1": 150.2,
                    "y1": 200.5,
                    "x2": 320.0,
                    "y2": 680.1
                },
                "metadata": {
                    "zone": "beverage_cooler",
                    "dwell_time_seconds": 4.5
                }
            }
        }