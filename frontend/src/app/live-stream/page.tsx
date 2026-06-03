// "use client";

// import { useAuth } from "@/hooks/useAuth";
// import { useWebSocket } from "@/hooks/useWebSocket";
// import Sidebar from "@/components/Sidebar";
// import TrackingCanvas from "@/components/TrackingCanvas";
// import { AlertTriangle, Activity } from "lucide-react";

// export default function LiveStreamPage() {
//   // 1. Enforce route protection (kicks to /login if no cookie)
//   const { isLoading: authLoading } = useAuth(true);
  
//   // 2. Connect to FastAPI WebSocket
//   const { isConnected, latestTelemetry, recentAlerts } = useWebSocket();

//   if (authLoading) return <div className="p-10 text-center">Verifying secure session...</div>;

//   return (
//     <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
//       <Sidebar />
      
//       <main className="ml-64 flex-1 p-8">
//         <div className="mb-8 flex items-center justify-between">
//           <div>
//             <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Live Tracking Matrix</h1>
//             <p className="text-slate-500 dark:text-slate-400">Real-time computer vision telemetry</p>
//           </div>
//           <div className={`flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium ${isConnected ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
//             <Activity className="h-4 w-4" />
//             {isConnected ? "System Online" : "Connection Lost"}
//           </div>
//         </div>

//         <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
//           {/* Main Video/Canvas Area */}
//           <div className="lg:col-span-2 space-y-4">
//             <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
//                {/* Fixed width/height relative to the typical YOLO 640x480 output scale */}
//                <div className="flex justify-center bg-black rounded-lg p-2">
//                  <TrackingCanvas telemetry={latestTelemetry} width={640} height={480} />
//                </div>
//             </div>
//           </div>

//           {/* Real-time Security Alerts Log */}
//           <div className="space-y-4">
//             <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
//               <AlertTriangle className="h-5 w-5 text-amber-500" />
//               Active Anomalies
//             </h3>
            
//             <div className="flex flex-col gap-3">
//               {recentAlerts.length === 0 ? (
//                 <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500 dark:border-slate-700">
//                   No recent security violations detected.
//                 </div>
//               ) : (
//                 recentAlerts.map((alert, i) => (
//                   <div key={i} className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900/50 dark:bg-red-950/20">
//                     <div className="flex justify-between">
//                       <span className="font-semibold text-red-700 dark:text-red-400 text-sm">{alert.event_type}</span>
//                       <span className="text-xs text-red-500">{new Date(alert.timestamp).toLocaleTimeString()}</span>
//                     </div>
//                     <p className="mt-1 text-xs text-red-600 dark:text-red-300">{alert.metadata.description}</p>
//                     <div className="mt-2 text-[10px] font-mono text-red-500">Target ID: #{alert.entity_id} | Zone: {alert.metadata.zone}</div>
//                   </div>
//                 ))
//               )}
//             </div>
//           </div>
//         </div>
//       </main>
//     </div>
//   );
// }

"use client";

import { useAuth } from "@/hooks/useAuth";
import { useWebSocket } from "@/hooks/useWebSocket";
import Sidebar from "@/components/Sidebar";
import TrackingCanvas from "@/components/TrackingCanvas";
import { AlertTriangle, Activity } from "lucide-react";

export default function LiveStreamPage() {
  // 1. Enforce route protection (kicks to /login if no cookie)
  const { isLoading: authLoading } = useAuth(true);
  
  // 2. Connect to FastAPI WebSocket
  const { isConnected, latestTelemetry, recentAlerts } = useWebSocket();

  if (authLoading) return <div className="p-10 text-center">Verifying secure session...</div>;

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar />
      
      <main className="ml-64 flex-1 p-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Live Tracking Matrix</h1>
            <p className="text-slate-500 dark:text-slate-400">Real-time computer vision telemetry</p>
          </div>
          <div className={`flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium ${isConnected ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
            <Activity className="h-4 w-4" />
            {isConnected ? "System Online" : "Connection Lost"}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          {/* Main Video/Canvas Area */}
          <div className="lg:col-span-2 space-y-4">
            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
               {/* Fixed width/height relative to the typical YOLO 640x480 output scale */}
               <div className="flex justify-center bg-black rounded-lg p-2">
                 <TrackingCanvas telemetry={latestTelemetry} width={640} height={480} />
               </div>
            </div>
          </div>

          {/* Real-time Security Alerts Log */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              Active Anomalies
            </h3>
            
            <div className="flex flex-col gap-3">
              {recentAlerts.length === 0 ? (
                <div className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500 dark:border-slate-700">
                  No recent security violations detected.
                </div>
              ) : (
                recentAlerts.map((alert, i) => (
                  <div key={i} className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900/50 dark:bg-red-950/20">
                    <div className="flex justify-between">
                      <span className="font-semibold text-red-700 dark:text-red-400 text-sm">{alert.event_type}</span>
                      <span className="text-xs text-red-500">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <p className="mt-1 text-xs text-red-600 dark:text-red-300">{alert.metadata.description}</p>
                    <div className="mt-2 text-[10px] font-mono text-red-500">Target ID: #{alert.entity_id} | Zone: {alert.metadata.zone}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}