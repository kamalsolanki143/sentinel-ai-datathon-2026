"use client";

import React, { useState } from "react";
import { Clock, ShieldAlert, FileCheck, MapPin, ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface TimelineEventItem {
  id: string;
  time: string;
  title: string;
  location: string;
  severity: "critical" | "high" | "medium";
  evidenceHash: string;
  details: string;
}

const mockTimelineEvents: TimelineEventItem[] = [
  {
    id: "TL-901",
    time: "23:42 EST",
    title: "Commercial Bank Vault Intrusion",
    location: "Sector 4 - First National Bank",
    severity: "critical",
    evidenceHash: "0x89f4...3a91",
    details: "Vault door motion sensor tripped. CCTV footage confirms 3 armed perpetrators wearing Viper Syndicate emblems.",
  },
  {
    id: "TL-902",
    time: "23:18 EST",
    title: "Getaway SUV Sighted at Toll Gate",
    location: "Sector 4 - Highway 101 North",
    severity: "high",
    evidenceHash: "0x44b2...99e2",
    details: "ANPR camera hit on License Plate XYZ-9082 matching vehicle registered to suspect Marcus Vance.",
  },
  {
    id: "TL-903",
    time: "22:50 EST",
    title: "Encrypted Cellular Signal Intercept",
    location: "Sector 2 - Harbor Warehouse B",
    severity: "medium",
    evidenceHash: "0x12c8...77f4",
    details: "Intercepted burst radio signal instructing getaway driver to hold position until 01:00 EST.",
  },
];

export default function TimelineWidget() {
  const [expandedId, setExpandedId] = useState<string | null>("TL-901");

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-md dark:shadow-xl space-y-4 transition-colors duration-300">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3.5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <Clock className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Incident Timeline Tracker</h3>
            <p className="text-[11px] text-slate-500 dark:text-white/40 mt-0.5">Sequential crime event logs & verified evidence hashes</p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-primary font-bold px-2 py-0.5 rounded bg-primary/10 border border-primary/20">
          3 EVENTS LOGGED
        </span>
      </div>

      {/* Timeline Stream */}
      <div className="relative border-l border-slate-200 dark:border-white/[0.1] ml-3.5 pl-4 space-y-4 my-2">
        {mockTimelineEvents.map((event) => {
          const isExpanded = expandedId === event.id;
          return (
            <div key={event.id} className="relative">
              {/* Pulsing Dot */}
              <div
                className={`absolute -left-[21px] top-1.5 h-3 w-3 rounded-full border-2 border-white dark:border-[#050816] ${
                  event.severity === "critical"
                    ? "bg-red-500 ring-4 ring-red-500/20"
                    : event.severity === "high"
                    ? "bg-amber-500"
                    : "bg-primary"
                }`}
              />

              <div
                onClick={() => toggleExpand(event.id)}
                className="p-3 rounded-2xl border border-slate-200/80 dark:border-white/[0.06] bg-slate-50/60 dark:bg-white/[0.02] hover:bg-slate-100 dark:hover:bg-white/[0.05] transition-all cursor-pointer space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-slate-400 dark:text-white/40 flex items-center gap-1">
                    <Clock className="h-3 w-3 text-primary" /> {event.time}
                  </span>
                  <span className={`px-2 py-0.5 rounded-full font-mono text-[9px] font-bold ${
                    event.severity === "critical"
                      ? "bg-red-500/10 text-red-500 border border-red-500/20"
                      : "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                  }`}>
                    {event.severity.toUpperCase()}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-900 dark:text-white">{event.title}</h4>
                  {isExpanded ? <ChevronUp className="h-3.5 w-3.5 text-slate-400" /> : <ChevronDown className="h-3.5 w-3.5 text-slate-400" />}
                </div>

                <p className="text-[11px] text-slate-500 dark:text-white/50 flex items-center gap-1">
                  <MapPin className="h-3 w-3 text-primary" /> {event.location}
                </p>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="pt-2 border-t border-slate-200/60 dark:border-white/[0.06] space-y-2 text-xs text-slate-700 dark:text-white/80"
                    >
                      <p className="leading-relaxed text-[11px]">{event.details}</p>
                      <div className="flex items-center gap-2 text-[10px] font-mono text-emerald-600 dark:text-emerald-400">
                        <FileCheck className="h-3.5 w-3.5" />
                        <span>CRYPTOGRAPHIC HASH: {event.evidenceHash}</span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
