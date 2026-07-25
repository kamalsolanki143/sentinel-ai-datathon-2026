"use client";

import React, { useState } from "react";
import {
  FileText,
  Activity,
  Network,
  AlertOctagon,
  ShieldAlert,
  Clock,
  FileCheck,
  ExternalLink,
  Eye,
  Video,
  FileCode,
} from "lucide-react";
import { motion } from "framer-motion";

interface EvidenceItem {
  id: string;
  type: string;
  name: string;
  timestamp: string;
  confidence: number;
  icon: React.ElementType;
}

interface TimelineEvent {
  id: string;
  time: string;
  title: string;
  location: string;
  severity: "high" | "medium" | "low";
}

interface CaseSummaryPanelProps {
  onQuickAction?: (actionType: string) => void;
}

export default function CaseSummaryPanel({ onQuickAction }: CaseSummaryPanelProps) {
  const [activeTab, setActiveTab] = useState<"summary" | "evidence" | "timeline">("summary");
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceItem | null>(null);
  const [alertTriggered, setAlertTriggered] = useState(false);

  const evidenceList: EvidenceItem[] = [
    { id: "EVD-901", type: "CCTV Video", name: "Cam_042_Downtown_Plaza.mp4", timestamp: "10m ago", confidence: 96, icon: Video },
    { id: "EVD-902", type: "ANPR Scan", name: "License_Plate_XYZ_9082.jpg", timestamp: "24m ago", confidence: 91, icon: Eye },
    { id: "EVD-903", type: "Cell Intercept", name: "Encrypted_Comm_772.log", timestamp: "1h ago", confidence: 88, icon: FileCode },
    { id: "EVD-904", type: "Ballistics", name: "9mm_Shell_Report.pdf", timestamp: "3h ago", confidence: 99, icon: FileCheck },
  ];

  const timelineEvents: TimelineEvent[] = [
    { id: "TL-1", time: "22:45", title: "Vehicle Gathering Detected", location: "Downtown Sector 4", severity: "medium" },
    { id: "TL-2", time: "23:12", title: "Silent Alarm - Commercial Vault", location: "First National Bank", severity: "high" },
    { id: "TL-3", time: "23:18", title: "Getaway Vehicle Sighted", location: "Highway 101 Northbound", severity: "high" },
    { id: "TL-4", time: "23:30", title: "Patrol Unit #14 Dispatched", location: "Sector 4 Intercept", severity: "low" },
  ];

  const handleAlert = () => {
    setAlertTriggered(true);
    onQuickAction?.("Emergency Alert");
    setTimeout(() => setAlertTriggered(false), 4000);
  };

  const tabs = ["summary", "evidence", "timeline"] as const;

  return (
    <div className="h-full flex flex-col bg-white dark:bg-[#050816] border-l border-slate-200/80 dark:border-white/[0.08] w-80 lg:w-84 overflow-hidden hidden lg:flex shadow-xl dark:shadow-2xl z-20 transition-colors duration-300">
      {/* Header */}
      <div className="p-3.5 border-b border-slate-200 dark:border-white/[0.08] bg-slate-50/80 dark:bg-[#0f172a]/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10 text-primary border border-primary/20">
            <ShieldAlert className="h-4 w-4" />
          </div>
          <div>
            <h2 className="font-bold text-xs text-slate-900 dark:text-white">Case Intelligence</h2>
            <p className="text-[9px] text-slate-500 dark:text-white/40 font-mono">ID: CAS-8924 • SECTOR 4</p>
          </div>
        </div>
        <span className="text-[9px] bg-red-500/10 text-red-500 dark:text-red-400 border border-red-500/20 px-2 py-0.5 rounded-full font-mono font-bold flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-red-500 dark:bg-red-400 animate-ping" />
          CRITICAL
        </span>
      </div>

      {/* Tabs Selector */}
      <div className="flex border-b border-slate-200 dark:border-white/[0.06] bg-slate-50/40 dark:bg-[#0f172a]/30 text-xs">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2.5 font-semibold uppercase tracking-wider text-[10px] transition-all border-b-2 ${
              activeTab === tab
                ? "border-primary text-primary bg-primary/5"
                : "border-transparent text-slate-500 dark:text-white/40 hover:text-slate-800 dark:hover:text-white/70"
            }`}
          >
            {tab === "evidence" ? `Evidence (${evidenceList.length})` : tab}
          </button>
        ))}
      </div>

      {/* Main Tab Content */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5 no-scrollbar">
        {activeTab === "summary" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3.5">
            {/* Primary Incident Card */}
            <div className="p-3.5 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-slate-50/60 dark:bg-[#0f172a]/80 backdrop-blur-xl space-y-3 shadow-sm dark:shadow-lg">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[9px] text-primary font-mono uppercase tracking-wider font-semibold">Active Dossier</span>
                  <h3 className="font-bold text-xs text-slate-900 dark:text-white mt-0.5">
                    Downtown Syndicate Commercial Vault Intrusion
                  </h3>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs pt-2.5 border-t border-slate-200 dark:border-white/[0.06]">
                <div>
                  <span className="text-slate-500 dark:text-white/30 block text-[10px]">Prime Suspect</span>
                  <span className="text-slate-800 dark:text-white/90 font-semibold text-[11px]">Marcus Vance</span>
                </div>
                <div>
                  <span className="text-slate-500 dark:text-white/30 block text-[10px]">Threat Index</span>
                  <span className="font-mono font-bold text-red-500 dark:text-red-400 text-[11px]">94 / 100</span>
                </div>
                <div>
                  <span className="text-slate-500 dark:text-white/30 block text-[10px]">Affiliation</span>
                  <span className="text-slate-700 dark:text-white/80 text-[11px]">Viper Syndicate</span>
                </div>
                <div>
                  <span className="text-slate-500 dark:text-white/30 block text-[10px]">Warrants</span>
                  <span className="text-amber-500 dark:text-amber-400 font-mono text-[11px] font-bold">4 Active</span>
                </div>
              </div>
            </div>

            {/* Risk Vector Progress Meter */}
            <div className="p-3.5 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-slate-50/60 dark:bg-[#0f172a]/80 backdrop-blur-xl space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-700 dark:text-white/70 flex items-center gap-1.5 font-semibold">
                  <Activity className="h-3.5 w-3.5 text-accent" /> Escalation Probability
                </span>
                <span className="text-red-500 dark:text-red-400 font-mono text-[10px] font-bold">HIGH (94%)</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-white/[0.06] h-2 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 h-full w-[94%] rounded-full shadow-lg shadow-red-500/20" />
              </div>
              <p className="text-[10px] text-slate-500 dark:text-white/40 leading-relaxed pt-1">
                Security Copilot models estimate a 94% likelihood of armed getaway activity within 2 hours.
              </p>
            </div>

            {/* Assigned Units */}
            <div className="p-3.5 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-slate-50/60 dark:bg-[#0f172a]/80 backdrop-blur-xl space-y-2">
              <h4 className="text-[10px] font-bold text-slate-400 dark:text-white/30 uppercase tracking-widest">
                Deployed Units
              </h4>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between items-center p-2 bg-white dark:bg-white/[0.03] rounded-xl border border-slate-200 dark:border-white/[0.06]">
                  <span className="text-slate-800 dark:text-white/80 font-medium">Strike Team Alpha</span>
                  <span className="text-emerald-600 dark:text-emerald-400 text-[10px] font-mono font-bold flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" /> DEPLOYED
                  </span>
                </div>
                <div className="flex justify-between items-center p-2 bg-white dark:bg-white/[0.03] rounded-xl border border-slate-200 dark:border-white/[0.06]">
                  <span className="text-slate-800 dark:text-white/80 font-medium">Cyber Intelligence Cell</span>
                  <span className="text-primary text-[10px] font-mono font-bold flex items-center gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" /> MONITORING
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === "evidence" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-2">
            {evidenceList.map((item) => (
              <div
                key={item.id}
                onClick={() => setSelectedEvidence(item)}
                className="p-3 rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-slate-50/60 dark:bg-[#0f172a]/80 hover:bg-slate-100 dark:hover:bg-white/[0.05] transition-all cursor-pointer group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-xl bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white transition-colors">
                      <item.icon className="h-4 w-4" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                        {item.name}
                      </h4>
                      <p className="text-[10px] text-slate-500 dark:text-white/40">{item.type} • {item.timestamp}</p>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    {item.confidence}%
                  </span>
                </div>
              </div>
            ))}

            {selectedEvidence && (
              <div className="mt-3 p-3 rounded-2xl border border-primary/30 bg-primary/5 text-xs space-y-2">
                <div className="flex justify-between items-center text-primary font-bold">
                  <span>{selectedEvidence.id}</span>
                  <button onClick={() => setSelectedEvidence(null)} className="text-slate-400 dark:text-white/30 hover:text-slate-800 dark:hover:text-white text-[10px]">
                    Dismiss
                  </button>
                </div>
                <p className="text-slate-600 dark:text-white/60 text-[11px]">
                  Verified evidence node linked to Marcus Vance. Hash signature verified on Sentinel Chain.
                </p>
                <button className="w-full py-1.5 bg-primary hover:bg-primary/90 text-white rounded-xl font-bold flex items-center justify-center gap-1 transition-colors text-xs">
                  <ExternalLink className="h-3 w-3" /> Inspect Cryptographic Hash
                </button>
              </div>
            )}
          </motion.div>
        )}

        {activeTab === "timeline" && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="relative border-l border-slate-200 dark:border-white/[0.1] ml-3 space-y-4 my-2 pl-4">
            {timelineEvents.map((evt) => (
              <div key={evt.id} className="relative">
                <div
                  className={`absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full ${
                    evt.severity === "high"
                      ? "bg-red-500 ring-4 ring-red-500/20"
                      : evt.severity === "medium"
                      ? "bg-amber-500"
                      : "bg-primary"
                  }`}
                />
                <div className="text-[10px] font-mono text-slate-400 dark:text-white/40 flex items-center gap-1">
                  <Clock className="h-3 w-3 text-primary" /> {evt.time}
                </div>
                <h4 className="text-xs font-semibold text-slate-800 dark:text-white/90 mt-0.5">{evt.title}</h4>
                <p className="text-[10px] text-slate-500 dark:text-white/40">{evt.location}</p>
              </div>
            ))}
          </motion.div>
        )}
      </div>

      {/* Quick Actions Panel */}
      <div className="p-3.5 border-t border-slate-200 dark:border-white/[0.08] bg-slate-50/60 dark:bg-[#0f172a]/60 space-y-2">
        <h4 className="text-[10px] font-bold text-slate-400 dark:text-white/30 uppercase tracking-widest">
          Tactical Actions
        </h4>

        {alertTriggered && (
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="p-2 bg-red-500/20 text-red-500 dark:text-red-400 rounded-xl text-xs font-bold flex items-center gap-2 border border-red-500/30 shadow-lg"
          >
            <ShieldAlert className="h-4 w-4 animate-bounce text-red-500 dark:text-red-400" />
            TACTICAL DISPATCH ALERT SENT
          </motion.div>
        )}

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => onQuickAction?.("Generate Report")}
            className="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-white dark:bg-white/[0.04] hover:bg-slate-100 dark:hover:bg-white/[0.08] text-slate-800 dark:text-white/80 rounded-xl text-xs font-semibold border border-slate-200 dark:border-white/[0.08] transition-all shadow-sm"
          >
            <FileText className="h-3.5 w-3.5 text-primary" /> Report
          </button>
          <button
            onClick={() => onQuickAction?.("Predict Crime")}
            className="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-white dark:bg-white/[0.04] hover:bg-slate-100 dark:hover:bg-white/[0.08] text-slate-800 dark:text-white/80 rounded-xl text-xs font-semibold border border-slate-200 dark:border-white/[0.08] transition-all shadow-sm"
          >
            <Activity className="h-3.5 w-3.5 text-accent" /> Predict
          </button>
          <button
            onClick={() => onQuickAction?.("Network Analysis")}
            className="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-white dark:bg-white/[0.04] hover:bg-slate-100 dark:hover:bg-white/[0.08] text-slate-800 dark:text-white/80 rounded-xl text-xs font-semibold border border-slate-200 dark:border-white/[0.08] transition-all shadow-sm"
          >
            <Network className="h-3.5 w-3.5 text-amber-500" /> Network
          </button>
          <button
            onClick={handleAlert}
            className="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-500 dark:text-red-400 rounded-xl text-xs font-bold border border-red-500/20 transition-all shadow-sm"
          >
            <AlertOctagon className="h-3.5 w-3.5 animate-pulse" /> Dispatch
          </button>
        </div>
      </div>
    </div>
  );
}
