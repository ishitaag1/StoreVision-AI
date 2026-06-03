"use client";

import { useState, useEffect, useRef } from "react";
import { WebSocketStreamMessage, StoreEvent, AnomalyAlert } from "@/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [latestTelemetry, setLatestTelemetry] = useState<StoreEvent | null>(null);
  const [recentAlerts, setRecentAlerts] = useState<AnomalyAlert[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(`${WS_URL}/ws/telemetry`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("📡 Connected to Store Intelligence Telemetry Stream");
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const payload: WebSocketStreamMessage = JSON.parse(event.data);
          if (payload.stream_type === "live_telemetry") {
            setLatestTelemetry(payload.data);
          } else if (payload.stream_type === "security_alert") {
            setRecentAlerts((prev) => [payload.data, ...prev].slice(0, 10));
          }
        } catch (error) {
          console.warn("Failed to parse incoming telemetry data");
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Attempt auto-reconnect silently every 3 seconds
        setTimeout(connect, 3000);
      };

      ws.onerror = (error) => {
        // Just quietly warn and close, no more red screens or fake simulations
        console.warn("Backend WebSocket unreachable. Awaiting real camera connection...");
        ws.close();
      };
    };

    connect();

    // Cleanup function when you navigate away from the page
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return { isConnected, latestTelemetry, recentAlerts };
}