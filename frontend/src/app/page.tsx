"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import Sidebar from "@/components/Sidebar";
import StatCard from "@/components/StatCard";
// IMPORT THE NEW FUNCTIONS
import { getOverviewMetrics, getAnomalies } from "@/services/analytics.service";
import { Users, AlertOctagon, Camera, Activity, BarChart3, ArrowRight, ShieldCheck } from "lucide-react";

export default function OverviewPage() {
  const { user, isLoading: authLoading } = useAuth(true);
  const [metrics, setMetrics] = useState<any>(null);
  const [anomalyCount, setAnomalyCount] = useState<number>(0);

  useEffect(() => {
    if (!authLoading) {
      // Fetch the main metrics
      getOverviewMetrics()
        .then(setMetrics)
        .catch((error) => console.error("Failed to load overview metrics", error));
      
      // Fetch the security flags/anomalies to get an accurate count
      getAnomalies()
        .then((anomalies) => setAnomalyCount(anomalies.length))
        .catch((error) => console.error("Failed to load anomalies", error));
    }
  }, [authLoading]);

  if (authLoading) return <div className="flex min-h-screen items-center justify-center text-slate-500">Verifying secure session...</div>;

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar />
      
      <main className="ml-64 flex-1 p-8">
        {/* Welcome Hero Section */}
        <div className="mb-10 rounded-2xl bg-indigo-600 p-8 text-white shadow-lg">
          <div className="flex items-center gap-3 text-indigo-200 mb-2">
            <ShieldCheck className="h-6 w-6" />
            <span className="font-medium tracking-wide uppercase text-sm">System Secure</span>
          </div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.username || "Admin"}</h1>
          <p className="mt-2 max-w-2xl text-indigo-100">
            The computer vision engine is active. Currently monitoring your local tracking pipelines and persisting telemetry to MongoDB.
          </p>
        </div>

        {/* High-Level Overview Metrics */}
        <div className="mb-10">
          <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">Live System Status</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard 
              title="Total Foot Traffic" 
              value={metrics?.total_foot_traffic ?? "Loading..."} 
              icon={Users} 
            />
            <StatCard 
              title="Active Security Flags" 
              value={anomalyCount.toString()} 
              icon={AlertOctagon} 
            />
            <StatCard 
              title="Conversion Rate" 
              value={metrics?.conversion_rate ? `${metrics.conversion_rate}%` : "Loading..."} 
              icon={Camera} 
            />
          </div>
        </div>

        {/* Quick Actions Matrix */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Link href="/live-stream" className="group block">
            <div className="rounded-xl border border-slate-200 bg-white p-6 transition-all hover:border-indigo-500 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-indigo-500">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400">
                <Activity className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">Live Telemetry</h3>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                View real-time YOLOv8 bounding boxes, entity tracking, and immediate security alerts streamed via WebSockets.
              </p>
              <div className="mt-4 flex items-center gap-2 text-sm font-medium text-indigo-600 dark:text-indigo-400">
                Open Matrix <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          </Link>

          <Link href="/analytics" className="group block">
            <div className="rounded-xl border border-slate-200 bg-white p-6 transition-all hover:border-emerald-500 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-emerald-500">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400">
                <BarChart3 className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">Business Intelligence</h3>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                Analyze aggregated historical data from MongoDB, view foot traffic trendlines, and evaluate spatial zone utilization.
              </p>
              <div className="mt-4 flex items-center gap-2 text-sm font-medium text-emerald-600 dark:text-emerald-400">
                View Analytics <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          </Link>
        </div>
      </main>
    </div>
  );
}