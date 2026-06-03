// src/services/analytics.service.ts
import { api } from "./api"; 

// 1. Overview Metrics 
export const getOverviewMetrics = async (storeId = "STORE_BLR_002") => {
    // 🔴 FIXED: Added /api back to the beginning of the path
    const response = await api.get(`/api/analytics/stores/${storeId}/metrics`);
    return response.data;
};

// 2. Conversion Funnel 
export const getFunnelData = async (storeId = "STORE_BLR_002") => {
    const response = await api.get(`/api/analytics/stores/${storeId}/funnel`);
    return response.data;
};

// 3. Zone Heatmap 
export const getZoneHeatmap = async (storeId = "STORE_BLR_002") => {
    const response = await api.get(`/api/analytics/stores/${storeId}/heatmap`);
    return response.data;
};

// 4. Operational Anomalies
export const getAnomalies = async (storeId = "STORE_BLR_002") => {
    const response = await api.get(`/api/analytics/stores/${storeId}/anomalies`);
    return response.data;
};