"use client";

import { useEffect, useRef } from "react";
import { StoreEvent } from "@/types";

interface TrackingCanvasProps {
  telemetry: StoreEvent | null;
  width?: number;
  height?: number;
}

export default function TrackingCanvas({ telemetry, width = 640, height = 480 }: TrackingCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear previous frame canvas overlays cleanly
    ctx.clearRect(0, 0, width, height);

    if (!telemetry || !telemetry.box) return;

    const { x1, y1, x2, y2 } = telemetry.box;
    const boxWidth = x2 - x1;
    const boxHeight = y2 - y1;

    // 1. Draw Bounding Box rectangle lines
    ctx.strokeStyle = "#4f46e5"; // Indigo-600 boundary marker
    ctx.lineWidth = 3;
    ctx.strokeRect(x1, y1, boxWidth, boxHeight);

    // 2. Draw Semi-transparent tracking overlay background
    ctx.fillStyle = "rgba(79, 70, 229, 0.1)";
    ctx.fillRect(x1, y1, boxWidth, boxHeight);

    // 3. Draw Descriptive Data Label Tags right above target boundaries
    const label = `ID: ${telemetry.entity_id} (${Math.round(telemetry.confidence * 100)}%)`;
    ctx.font = "12px sans-serif";
    const textWidth = ctx.measureText(label).width;

    ctx.fillStyle = "#4f46e5";
    ctx.fillRect(x1 - 1.5, y1 - 20, textWidth + 12, 20);

    ctx.fillStyle = "#ffffff";
    ctx.fillText(label, x1 + 4, y1 - 6);
  }, [telemetry, width, height]);

  return (
    <div className="relative overflow-hidden rounded-xl bg-slate-950" style={{ width, height }}>
      {/* Fallback canvas layout mimicking a raw surveillance display matrix */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
        <p className="text-sm font-medium">Surveillance Video Underlay Feed</p>
        <p className="text-xs text-slate-600 mt-1">Overlay canvas active</p>
      </div>

      {/* Interactive frame painting plane */}
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="absolute inset-0 z-10 pointer-events-none"
      />
    </div>
  );
}