export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface StoreEvent {
  id?: string;
  camera_id: string;
  timestamp: string; 
  event_type: "person_tracking" | string;
  entity_id: number;
  confidence: number;
  box: BoundingBox;
  metadata: {
    zone: string;
    dwell_time_seconds?: number;
    [key: string]: any;
  };
}

export interface AnomalyAlert {
  id?: string;
  camera_id: string;
  timestamp: string;
  event_type: "anomaly_loitering" | string;
  entity_id: number;
  confidence: number;
  box?: BoundingBox;
  metadata: {
    zone: string;
    duration_seconds: number;
    alert_level: "low" | "medium" | "high";
    description: string;
  };
}

export type WebSocketStreamMessage =
  | {
      stream_type: "live_telemetry";
      data: StoreEvent;
    }
  | {
      stream_type: "security_alert";
      data: AnomalyAlert;
    };