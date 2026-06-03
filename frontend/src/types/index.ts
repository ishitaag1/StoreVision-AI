export interface User {
  username: string;
  email: string;
}

export interface ApiResponse<T> {
  status: "success" | "error";
  message?: string;
  data?: T;
}

export interface PaginatedResponse<T> {
  status: "success";
  meta: {
    total_records: number;
    page: number;
    limit: number;
    total_pages: number;
  };
  data: T[];
}

export interface DashboardOverviewMetrics {
  foot_traffic_24h: number;
  alerts_triggered_24h: number;
  active_camera_feeds: number;
}

export * from "./telemetry";