"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import {
  BellRing,
  ShieldAlert,
  AlertTriangle,
  Clock,
  Radio,
  MapPin,
  Volume2,
  Smartphone,
  Check,
  Navigation,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import PageHeader from "@/components/Common/PageHeader";
import MetricCard from "@/components/Cards/MetricCard";
import StatusBadge from "@/components/Common/StatusBadge";
import ConfirmDialog from "@/components/Common/ConfirmDialog";
import { alertService, AlertItem } from "@/services/alertService";

const HeatMap = dynamic(() => import("@/components/HeatMap/HeatMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-slate-100 dark:bg-[#050816] animate-pulse rounded-2xl flex items-center justify-center border border-slate-200 dark:border-white/[0.08]">
      <span className="text-slate-500 dark:text-white/40 text-xs font-mono flex items-center gap-2">
        <Radio className="h-4 w-4 animate-spin text-red-500 dark:text-red-400" />
        CONNECTING TACTICAL GEOLOCATION RADAR...
      </span>
    </div>
  ),
});

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [priorityFilter, setPriorityFilter] = useState("All");
  const [pushEnabled, setPushEnabled] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [emergencyAlertActive, setEmergencyAlertActive] = useState(false);
  const [confirmBroadcastModal, setConfirmBroadcastModal] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    setLoading(true);
    const data = await alertService.getAlerts();
    setAlerts(data);
    setLoading(false);
  };

  const handleAcknowledge = async (id: string) => {
    await alertService.acknowledgeAlert(id);
    setAlerts((prev) =>
      prev.map((alt) => (alt.id === id ? { ...alt, status: "Acknowledged" } : alt))
    );
    showToast(`Alert ${id} acknowledged by Command Officer.`);
  };

  const handleTriggerEmergencyBroadcast = () => {
    setConfirmBroadcastModal(false);
    setEmergencyAlertActive(true);
    showToast("EMERGENCY DEFCON 1 BROADCAST DISPATCHED TO ALL PATROLS!");
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const filteredAlerts = alerts.filter((alt) => {
    if (priorityFilter !== "All" && alt.priority !== priorityFilter) return false;
    return true;
  });

  const criticalCount = alerts.filter((a) => a.priority === "Critical").length;
  const activeCount = alerts.filter((a) => a.status === "Active").length;

  return (
    <div className="space-y-6">
      {/* Toast Alert */}
      <AnimatePresence>
        {toastMessage && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-20 right-6 z-50 p-3.5 bg-red-500/20 text-red-600 dark:text-red-400 border border-red-500/30 rounded-2xl shadow-2xl font-mono text-xs font-bold flex items-center gap-2 backdrop-blur-xl"
          >
            <Radio className="h-4 w-4 animate-ping text-red-500 dark:text-red-400" />
            {toastMessage}
          </motion.div>
        )}
      </AnimatePresence>

      <PageHeader
        title="Real-Time Threat Feeds & Emergency Response"
        subtitle="Live tactical alert stream, automated dispatch triggers, and emergency sector notifications."
        icon={BellRing}
        statusBadge={<StatusBadge status={`${criticalCount} CRITICAL THREATS`} variant="danger" pulse />}
      >
        <button
          onClick={() => setConfirmBroadcastModal(true)}
          className="px-4 py-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-600/90 hover:to-rose-600/90 text-white font-bold text-xs rounded-xl shadow-lg shadow-red-600/30 flex items-center gap-2 transition-all animate-pulse"
        >
          <ShieldAlert className="h-4 w-4" /> Trigger Emergency Broadcast
        </button>
      </PageHeader>

      {/* Emergency Active Banner */}
      <AnimatePresence>
        {emergencyAlertActive && (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            className="p-4 rounded-2xl bg-red-500/15 border border-red-500/30 text-red-600 dark:text-red-400 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-2xl"
          >
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-red-500 text-white shadow-lg shadow-red-500/40">
                <Radio className="h-5 w-5 animate-ping" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white font-mono">DEFCON 1 EMERGENCY BROADCAST ACTIVE</h3>
                <p className="text-xs text-red-700 dark:text-red-300/80 mt-0.5">All tactical units instructed to enter high-visibility alert mode.</p>
              </div>
            </div>
            <button
              onClick={() => setEmergencyAlertActive(false)}
              className="px-3.5 py-1.5 rounded-xl bg-slate-900 dark:bg-white/[0.08] hover:bg-slate-800 dark:hover:bg-white/[0.15] text-white text-xs font-bold border border-slate-700 dark:border-white/10 transition-colors shrink-0"
            >
              Cancel Broadcast
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Threat Alerts"
          value={activeCount}
          icon={AlertTriangle}
          trend="up"
          change="Requires Response"
          variant="danger"
        />
        <MetricCard
          title="Critical Priority"
          value={criticalCount}
          icon={ShieldAlert}
          trend="up"
          change="High Risk"
          variant="warning"
        />
        <MetricCard
          title="Dispatched Patrols"
          value="42 Units"
          icon={Navigation}
          trend="neutral"
          change="En Route"
          variant="primary"
        />
        <MetricCard
          title="System Sound Alarm"
          value={soundEnabled ? "ENABLED" : "MUTED"}
          icon={Volume2}
          trend="neutral"
          change="24/7 Monitoring"
          variant="accent"
        />
      </div>

      {/* Controls Bar */}
      <div className="p-4 rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4 shadow-sm dark:shadow-xl transition-colors duration-300">
        <div className="flex items-center gap-2 text-xs font-semibold">
          <span className="text-slate-400 dark:text-white/40 uppercase tracking-wider text-[10px] mr-2">Filter Priority:</span>
          {(["All", "Critical", "High", "Medium"] as const).map((pr) => (
            <button
              key={pr}
              onClick={() => setPriorityFilter(pr)}
              className={`px-3 py-1.5 rounded-xl transition-all ${
                priorityFilter === pr
                  ? "bg-primary text-white shadow font-bold"
                  : "bg-slate-100 dark:bg-white/[0.04] text-slate-600 dark:text-white/50 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-white/[0.06]"
              }`}
            >
              {pr}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-4 text-xs font-semibold">
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border transition-all ${
              soundEnabled
                ? "bg-primary/10 text-primary border-primary/30"
                : "bg-slate-100 dark:bg-white/[0.04] text-slate-500 dark:text-white/40 border-slate-200 dark:border-white/[0.08]"
            }`}
          >
            <Volume2 className="h-4 w-4" /> Sound Alarm: {soundEnabled ? "ON" : "OFF"}
          </button>
          <button
            onClick={() => setPushEnabled(!pushEnabled)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border transition-all ${
              pushEnabled
                ? "bg-accent/10 text-accent border-accent/30"
                : "bg-slate-100 dark:bg-white/[0.04] text-slate-500 dark:text-white/40 border-slate-200 dark:border-white/[0.08]"
            }`}
          >
            <Smartphone className="h-4 w-4" /> Push Feed: {pushEnabled ? "ON" : "OFF"}
          </button>
        </div>
      </div>

      {/* Main Grid: Alerts Stream vs Radar Map */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts Stream List (2 Cols) */}
        <div className="lg:col-span-2 space-y-3.5">
          {filteredAlerts.map((alt) => (
            <div
              key={alt.id}
              className={`p-4 rounded-2xl border backdrop-blur-xl transition-all space-y-3 shadow-sm dark:shadow-xl ${
                alt.priority === "Critical"
                  ? "border-red-500/30 bg-red-500/5 hover:border-red-500/50"
                  : "border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 hover:border-slate-300 dark:hover:border-white/20"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2.5 rounded-xl border shadow-md ${
                    alt.priority === "Critical"
                      ? "bg-red-500/10 text-red-500 dark:text-red-400 border-red-500/30"
                      : "bg-amber-500/10 text-amber-500 dark:text-amber-400 border-amber-500/30"
                  }`}>
                    <AlertTriangle className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-slate-900 dark:text-white">{alt.title}</h3>
                    <p className="text-xs text-slate-500 dark:text-white/50 mt-0.5 flex items-center gap-2 font-mono">
                      <span>{alt.id}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1"><MapPin className="h-3 w-3 text-primary" /> {alt.location}</span>
                    </p>
                  </div>
                </div>

                <StatusBadge
                  status={alt.status.toUpperCase()}
                  variant={alt.status === "Active" ? "danger" : "success"}
                  pulse={alt.status === "Active"}
                />
              </div>

              <p className="text-xs text-slate-700 dark:text-white/70 leading-relaxed bg-slate-50 dark:bg-white/[0.02] p-3 rounded-xl border border-slate-200 dark:border-white/[0.04]">
                {alt.description}
              </p>

              <div className="pt-2 flex items-center justify-between border-t border-slate-100 dark:border-white/[0.06] text-xs">
                <span className="text-slate-400 dark:text-white/40 font-mono text-[10px] flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {alt.timestamp}
                </span>

                <div className="flex items-center gap-2">
                  {alt.status === "Active" && (
                    <button
                      onClick={() => handleAcknowledge(alt.id)}
                      className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors"
                    >
                      <Check className="h-3.5 w-3.5" /> Acknowledge Alert
                    </button>
                  )}
                  <button
                    onClick={() => showToast(`Dispatching Tactical Patrol Unit to ${alt.location}`)}
                    className="px-3 py-1.5 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors"
                  >
                    <Navigation className="h-3.5 w-3.5" /> Dispatch Patrol Unit
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Tactical Map Overlay (1 Col) */}
        <div className="lg:col-span-1 rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-sm dark:shadow-xl space-y-4 flex flex-col justify-between transition-colors duration-300">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Radio className="h-4 w-4 text-red-500 dark:text-red-400 animate-pulse" /> Tactical Geolocation Radar
            </h3>
            <p className="text-xs text-slate-500 dark:text-white/40 mt-1">Real-time alert locations & patrol dispatch radii</p>
          </div>

          <div className="h-[420px] w-full rounded-xl overflow-hidden relative">
            <HeatMap />
          </div>
        </div>
      </div>

      {/* Confirmation Dialog for Emergency Broadcast */}
      <ConfirmDialog
        isOpen={confirmBroadcastModal}
        title="Trigger Emergency DEFCON 1 Broadcast?"
        description="This will send an emergency high-priority warning signal to all deployed officers and dispatch centers across all 4 sectors."
        confirmText="Broadcast Emergency Warning"
        onConfirm={handleTriggerEmergencyBroadcast}
        onCancel={() => setConfirmBroadcastModal(false)}
        variant="danger"
      />
    </div>
  );
}
