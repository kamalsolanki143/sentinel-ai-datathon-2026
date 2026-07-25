"use client";

import React from "react";
import dynamic from "next/dynamic";
import {
  AlertTriangle,
  Shield,
  Users,
  Activity,
  FileWarning,
  MapPin,
  Sparkles,
  ChevronRight,
  ShieldAlert,
  Radio,
  Clock,
  Sliders,
} from "lucide-react";
import MetricCard from "@/components/Cards/MetricCard";
import CrimeTrendChart from "@/components/Charts/CrimeTrendChart";
import PageHeader from "@/components/Common/PageHeader";
import StatusBadge from "@/components/Common/StatusBadge";
import CommandHero from "@/components/Dashboard/CommandHero";
import AIInsightsFeed from "@/components/Dashboard/AIInsightsFeed";
import TimelineWidget from "@/components/Dashboard/TimelineWidget";
import NetworkSnapshotWidget from "@/components/Dashboard/NetworkSnapshotWidget";
import LiveActivityStream from "@/components/Dashboard/LiveActivityStream";
import QuickActionPanel from "@/components/Dashboard/QuickActionPanel";
import IncidentsTable from "@/components/Dashboard/IncidentsTable";
import FloatingCopilotWidget from "@/components/Dashboard/FloatingCopilotWidget";
import { motion } from "framer-motion";

const HeatMap = dynamic(() => import("@/components/HeatMap/HeatMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-slate-100 dark:bg-[#050816] animate-pulse rounded-2xl flex items-center justify-center border border-slate-200 dark:border-white/[0.08]">
      <span className="text-slate-500 dark:text-white/40 text-xs font-mono flex items-center gap-2">
        <Activity className="h-4 w-4 animate-spin text-primary" />
        LOADING SPATIAL HEATMAP MODEL...
      </span>
    </div>
  ),
});

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] as const } },
};

export default function DashboardPage() {
  return (
    <div className="space-y-6 pb-12">
      {/* 1. Command Hero Header */}
      <CommandHero />

      {/* 2. Primary KPI Metrics Grid */}
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <motion.div variants={item}>
          <MetricCard
            title="Total Active Incidents"
            value="142"
            change="+4.2%"
            trend="up"
            icon={ShieldAlert}
            status="critical"
            sparklineData={[30, 45, 60, 52, 75, 90, 142]}
          />
        </motion.div>
        <motion.div variants={item}>
          <MetricCard
            title="AI Model Precision"
            value="99.8%"
            change="+0.6%"
            trend="up"
            icon={Sparkles}
            status="success"
            sparklineData={[94, 95, 97, 98, 98.5, 99.2, 99.8]}
          />
        </motion.div>
        <motion.div variants={item}>
          <MetricCard
            title="Mapped Syndicate Entities"
            value="1,204"
            change="+12 nodes"
            trend="up"
            icon={Users}
            status="neutral"
            sparklineData={[1100, 1120, 1150, 1170, 1190, 1200, 1204]}
          />
        </motion.div>
        <motion.div variants={item}>
          <MetricCard
            title="Avg Response Latency"
            value="1.8m"
            change="-18.4%"
            trend="down"
            icon={Activity}
            status="success"
            sparklineData={[3.2, 2.9, 2.5, 2.2, 2.0, 1.9, 1.8]}
          />
        </motion.div>
      </motion.div>

      {/* 3. Main Center Split Section: Spatial Map & AI Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Spatial Heatmap Matrix (2 Cols) */}
        <div className="lg:col-span-2 rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-md dark:shadow-xl space-y-4 flex flex-col justify-between transition-colors duration-300">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3.5">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
                <MapPin className="h-4 w-4" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                  Spatial Incident Radar Matrix
                  <StatusBadge variant="critical" pulse>LIVE FEED</StatusBadge>
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-white/40 mt-0.5">
                  Multi-layer crime density map & tactical unit vectors
                </p>
              </div>
            </div>
            <span className="text-[10px] font-mono text-slate-400 dark:text-white/40">
              SECTOR 4 DOWNTOWN
            </span>
          </div>

          <div className="h-[400px] w-full rounded-2xl overflow-hidden border border-slate-200/80 dark:border-white/[0.08]">
            <HeatMap height="100%" />
          </div>
        </div>

        {/* AI Insights & Pattern Feed (1 Col) */}
        <div className="space-y-6">
          <AIInsightsFeed />
          <QuickActionPanel />
        </div>
      </div>

      {/* 4. Secondary Grid: Crime Trends & Incident Timeline & Network Snapshot */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <CrimeTrendChart />
        <TimelineWidget />
        <div className="space-y-6">
          <NetworkSnapshotWidget />
          <LiveActivityStream />
        </div>
      </div>

      {/* 5. Enterprise Active Incidents Table */}
      <IncidentsTable />

      {/* 6. Persistent Floating AI Copilot Assistant */}
      <FloatingCopilotWidget />
    </div>
  );
}
