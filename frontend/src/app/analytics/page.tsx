// "use client";

// import { useEffect, useState } from "react";
// import { useAuth } from "@/hooks/useAuth";
// import Sidebar from "@/components/Sidebar";
// import StatCard from "@/components/StatCard";
// import { analyticsService, TrafficTrendItem, ZoneDistributionItem } from "@/services/analyticsService";
// import { DashboardOverviewMetrics } from "@/types";
// import { Users, AlertOctagon, Camera } from "lucide-react";
// import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// export default function AnalyticsPage() {
//   const { isLoading: authLoading } = useAuth(true);
//   const [metrics, setMetrics] = useState<DashboardOverviewMetrics | null>(null);
//   const [trafficData, setTrafficData] = useState<TrafficTrendItem[]>([]);
//   const [zoneData, setZoneData] = useState<ZoneDistributionItem[]>([]);

//   useEffect(() => {
//     async function loadData() {
//       try {
//         const [overview, trends, zones] = await Promise.all([
//           analyticsService.getOverviewMetrics(),
//           analyticsService.getTrafficTrends(),
//           analyticsService.getZoneDistributions()
//         ]);
//         setMetrics(overview);
//         setTrafficData(trends);
//         setZoneData(zones);
//       } catch (error) {
//         console.error("Failed to fetch analytics:", error);
//       }
//     }
//     // Only load if not trapped in auth loading state
//     if (!authLoading) loadData();
//   }, [authLoading]);

//   if (authLoading) return <div className="p-10 text-center">Verifying secure session...</div>;

//   return (
//     <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
//       <Sidebar />
      
//       <main className="ml-64 flex-1 p-8">
//         <div className="mb-8">
//           <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Business Intelligence</h1>
//           <p className="text-slate-500 dark:text-slate-400">Historical performance and operational metrics (Last 24H)</p>
//         </div>

//         {/* Top Metric Cards */}
//         <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
//           <StatCard 
//             title="Total Foot Traffic" 
//             value={metrics?.foot_traffic_24h || 0} 
//             icon={Users} 
//           />
//           <StatCard 
//             title="Triggered Alerts" 
//             value={metrics?.alerts_triggered_24h || 0} 
//             icon={AlertOctagon} 
//           />
//           <StatCard 
//             title="Active Camera Feeds" 
//             value={metrics?.active_camera_feeds || 0} 
//             icon={Camera} 
//           />
//         </div>

//         {/* Charts Matrix */}
//         <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
//           {/* Traffic Trend Line Chart */}
//           <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
//             <h3 className="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Hourly Traffic Volume</h3>
//             <div className="h-72 w-full">
//               <ResponsiveContainer width="100%" height="100%">
//                 <LineChart data={trafficData}>
//                   <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.2} />
//                   <XAxis dataKey="hour" tickFormatter={(tick) => `${tick}:00`} stroke="#64748b" fontSize={12} />
//                   <YAxis stroke="#64748b" fontSize={12} />
//                   <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
//                   <Line type="monotone" dataKey="count" stroke="#4f46e5" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
//                 </LineChart>
//               </ResponsiveContainer>
//             </div>
//           </div>

//           {/* Spatial Distribution Bar Chart */}
//           <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
//             <h3 className="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Zone Dwell Density</h3>
//             <div className="h-72 w-full">
//               <ResponsiveContainer width="100%" height="100%">
//                 <BarChart data={zoneData} layout="vertical" margin={{ left: 20 }}>
//                   <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#334155" opacity={0.2} />
//                   <XAxis type="number" stroke="#64748b" fontSize={12} />
//                   <YAxis type="category" dataKey="zone" stroke="#64748b" fontSize={12} width={100} />
//                   <Tooltip cursor={{ fill: 'rgba(79, 70, 229, 0.05)' }} contentStyle={{ borderRadius: '8px', border: 'none' }} />
//                   <Bar dataKey="value" fill="#4f46e5" radius={[0, 4, 4, 0]} />
//                 </BarChart>
//               </ResponsiveContainer>
//             </div>
//           </div>
//         </div>
//       </main>
//     </div>
//   );
// }

"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import Sidebar from "@/components/Sidebar";
import StatCard from "@/components/StatCard";
// 1. IMPORT THE NEW SERVICE FUNCTIONS DIRECTLY
import { 
  getOverviewMetrics, 
  getFunnelData, 
  getZoneHeatmap 
} from "@/services/analytics.service";
import { DashboardOverviewMetrics } from "@/types";
import { Users, AlertOctagon, Camera } from "lucide-react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export default function AnalyticsPage() {
  const { isLoading: authLoading } = useAuth(true);
  const [metrics, setMetrics] = useState<DashboardOverviewMetrics | null>(null);
  
  // 2. UPDATE STATE TO HOLD OUR NEW FUNNEL AND HEATMAP DATA
  const [funnelData, setFunnelData] = useState<any[]>([]);
  const [zoneData, setZoneData] = useState<any[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        // 3. CALL THE NEW ENDPOINTS CONCURRENTLY
        const [overview, funnel, heatmap] = await Promise.all([
          getOverviewMetrics(),
          getFunnelData(),
          getZoneHeatmap()
        ]);
        
        setMetrics(overview);
        // Map funnel data to match chart requirements
        setFunnelData(funnel.stages || []);
        // Map heatmap data
        setZoneData(heatmap || []);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
      }
    }
    
    if (!authLoading) {
      loadData();
    }
  }, [authLoading]);

  // If loading, you can render a spinner here
  if (authLoading) return <div className="p-8 text-white">Loading Auth...</div>;

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar />
      <main className="ml-64 flex-1 overflow-y-auto p-8">
        <div className="mx-auto max-w-7xl">
          <h1 className="mb-8 text-3xl font-bold text-slate-900 dark:text-white">Store Analytics</h1>

          {/* Overview Metrics Cards */}
          <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard 
              title="Foot Traffic" 
              value={metrics?.total_foot_traffic?.toString() || "0"} 
              icon={Users} 
            />
            <StatCard 
              title="Conversion Rate" 
              value={`${metrics?.conversion_rate || 0}%`} 
              icon={Camera} 
            />
            <StatCard 
              title="Avg Dwell Time" 
              value={`${(((metrics as any)?.avg_dwell_ms ?? 0) / 1000).toFixed(1)}s`} 
              icon={AlertOctagon} 
            />
            <StatCard 
              title="Queue Depth" 
              value={(metrics as any)?.queue_depth?.toString() || "0"} 
              icon={Users} 
            />
          </div>

          <div className="mb-8 grid gap-6 lg:grid-cols-2">
            {/* Conversion Funnel Line Chart (Replaced Traffic Trend) */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h3 className="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Conversion Funnel Drop-off</h3>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  {/* 4. POINT CHART TO FUNNEL DATA */}
                  <LineChart data={funnelData} margin={{ top: 10, right: 30, left: -20, bottom: 30 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" opacity={0.2} />
                    <XAxis 
                      dataKey="stage" 
                      stroke="#64748b" 
                      fontSize={11} 
                      tickMargin={25} 
                      interval={0} 
                      angle={-15} 
                      textAnchor="end" 
                      height={60}
                    />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                    <Line type="monotone" dataKey="count" stroke="#4f46e5" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Spatial Distribution Bar Chart */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
              <h3 className="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Zone Dwell Density</h3>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  {/* 6. POINT CHART TO ZONE DATA */}
                  <BarChart data={zoneData} layout="vertical" margin={{ left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#334155" opacity={0.2} />
                    <XAxis type="number" stroke="#64748b" fontSize={12} />
                    {/* 7. UPDATE Y-AXIS TO 'zone_id' */}
                    <YAxis type="category" dataKey="zone_id" stroke="#64748b" fontSize={12} width={100} />
                    <Tooltip cursor={{ fill: 'rgba(79, 70, 70, 0.1)' }} contentStyle={{ borderRadius: '8px', border: 'none' }} />
                    {/* 8. UPDATE BAR DATA KEY TO 'visit_count' */}
                    <Bar dataKey="visit_count" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={24} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}