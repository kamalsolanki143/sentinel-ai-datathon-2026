"use client";

import React from "react";
import dynamic from "next/dynamic";
import { AlertTriangle, Shield, Users, Activity, FileWarning, Eye } from "lucide-react";
import MetricCard from "@/components/Cards/MetricCard";
import CrimeTrendChart from "@/components/Charts/CrimeTrendChart";
import { motion } from "framer-motion";

// Dynamic import for Leaflet map to avoid SSR issues
const HeatMap = dynamic(() => import("@/components/HeatMap/HeatMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-muted/20 animate-pulse rounded-lg flex items-center justify-center border border-border">
      <span className="text-muted-foreground text-sm flex items-center gap-2">
        <Activity className="h-4 w-4 animate-spin" />
        Initializing Geolocation Module...
      </span>
    </div>
  ),
});

export default function DashboardPage() {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Command Center</h1>
          <p className="text-muted-foreground mt-1">
            Real-time intelligence and threat assessment overview.
          </p>
        </div>
        <div className="flex gap-2">
          <div className="px-3 py-1.5 bg-destructive/10 text-destructive border border-destructive/20 rounded-md text-sm font-medium flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-destructive"></span>
            </span>
            2 Active High-Risk Alerts
          </div>
        </div>
      </div>

      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <MetricCard
          title="Active Incidents"
          value={142}
          icon={AlertTriangle}
          trend="up"
          trendValue="+12%"
          description="vs last 24h"
          variant="danger"
        />
        <MetricCard
          title="Officers Deployed"
          value={845}
          icon={Shield}
          trend="up"
          trendValue="+5%"
          description="vs last shift"
          variant="success"
        />
        <MetricCard
          title="AI Risk Predictions"
          value={38}
          icon={Activity}
          trend="down"
          trendValue="-2%"
          description="high probability"
          variant="warning"
        />
        <MetricCard
          title="Persons of Interest"
          value="1,204"
          icon={Users}
          trend="neutral"
          trendValue="0%"
          description="tracked currently"
        />
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[450px]">
        <motion.div 
          className="lg:col-span-2 rounded-xl border border-border bg-card shadow-sm flex flex-col overflow-hidden relative"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="p-4 border-b border-border bg-card/50 backdrop-blur-sm absolute top-0 w-full z-10 flex justify-between items-center">
            <h3 className="font-semibold flex items-center gap-2">
              <Eye className="h-4 w-4 text-primary" />
              Live Threat Heatmap
            </h3>
            <div className="text-xs text-muted-foreground bg-background/80 px-2 py-1 rounded">
              Sector 4 - Alpha
            </div>
          </div>
          <div className="flex-1 w-full h-full pt-14">
            <HeatMap />
          </div>
        </motion.div>

        <motion.div 
          className="rounded-xl border border-border bg-card shadow-sm p-6 flex flex-col"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <FileWarning className="h-4 w-4 text-primary" />
              24h Threat Trend vs Prediction
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              AI model tracking actual incident volume against forecasted baseline.
            </p>
          </div>
          <div className="flex-1 w-full">
            <CrimeTrendChart />
          </div>
        </motion.div>
      </div>

      <motion.div 
        className="rounded-xl border border-border bg-card shadow-sm overflow-hidden"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <div className="p-4 border-b border-border flex justify-between items-center bg-muted/10">
          <h3 className="font-semibold">Recent High-Priority Cases</h3>
          <button className="text-sm text-primary hover:underline">View All</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground bg-muted/20 border-b border-border">
              <tr>
                <th className="px-6 py-3 font-medium">Case ID</th>
                <th className="px-6 py-3 font-medium">Type</th>
                <th className="px-6 py-3 font-medium">Location</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium">AI Risk Score</th>
                <th className="px-6 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {[
                { id: "CAS-8924", type: "Armed Robbery", loc: "Sector 4, Downtown", status: "Active", risk: 94 },
                { id: "CAS-8923", type: "Suspicious Activity", loc: "Sector 2, Port", status: "Investigating", risk: 78 },
                { id: "CAS-8921", type: "Vehicle Theft", loc: "Sector 7, Suburbs", status: "Resolved", risk: 42 },
                { id: "CAS-8919", type: "Assault", loc: "Sector 3, Market", status: "Active", risk: 88 },
              ].map((row, i) => (
                <tr key={i} className="hover:bg-muted/10 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs">{row.id}</td>
                  <td className="px-6 py-4 font-medium">{row.type}</td>
                  <td className="px-6 py-4 text-muted-foreground">{row.loc}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      row.status === 'Active' ? 'bg-destructive/10 text-destructive' :
                      row.status === 'Resolved' ? 'bg-success/10 text-success' : 'bg-warning/10 text-warning'
                    }`}>
                      {row.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${row.risk > 80 ? 'bg-destructive' : row.risk > 50 ? 'bg-warning' : 'bg-success'}`}
                          style={{ width: `${row.risk}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium">{row.risk}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-primary hover:text-primary/80 transition-colors">Details</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
}
