"use client";

import React, { useState, useEffect } from "react";
import { Radio, ShieldAlert, CheckCircle2, Navigation, AlertTriangle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface StreamItem {
  id: string;
  time: string;
  text: string;
  type: "critical" | "dispatch" | "success" | "warning";
}

const initialStream: StreamItem[] = [
  { id: "S-1", time: "Just now", text: "Patrol Unit #14 dispatched to Sector 4 Commercial Vault.", type: "dispatch" },
  { id: "S-2", time: "2m ago", text: "CCTV facial recognition matched Marcus Vance near Sector 4.", type: "critical" },
  { id: "S-3", time: "6m ago", text: "ANPR scan hit: License Plate XYZ-9082 confirmed on Corridor 101.", type: "warning" },
  { id: "S-4", time: "12m ago", text: "Security Copilot generated dossier #REP-9041.", type: "success" },
];

export default function LiveActivityStream() {
  const [stream, setStream] = useState<StreamItem[]>(initialStream);

  useEffect(() => {
    const interval = setInterval(() => {
      const newItem: StreamItem = {
        id: `S-${Date.now()}`,
        time: "Just now",
        text: `Automated telemetry tick: Patrol Unit #${Math.floor(10 + Math.random() * 80)} location verified.`,
        type: Math.random() > 0.5 ? "dispatch" : "success",
      };
      setStream((prev) => [newItem, ...prev.slice(0, 4)]);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-md dark:shadow-xl space-y-3.5 transition-colors duration-300">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3">
        <div className="flex items-center gap-2">
          <Radio className="h-4 w-4 text-emerald-500 animate-pulse" />
          <h3 className="font-bold text-xs text-slate-900 dark:text-white uppercase tracking-wider font-mono">
            Live Activity Stream
          </h3>
        </div>
        <span className="text-[9px] font-mono text-emerald-600 dark:text-emerald-400 font-bold px-1.5 py-0.5 rounded bg-emerald-500/10">
          STREAMING 24/7
        </span>
      </div>

      <div className="space-y-2 max-h-56 overflow-y-auto no-scrollbar">
        <AnimatePresence>
          {stream.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0 }}
              className="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.04] text-xs flex items-start gap-2.5"
            >
              {item.type === "critical" && <ShieldAlert className="h-4 w-4 text-red-500 shrink-0 mt-0.5" />}
              {item.type === "dispatch" && <Navigation className="h-4 w-4 text-primary shrink-0 mt-0.5" />}
              {item.type === "warning" && <AlertTriangle className="h-4 w-4 text-amber-500 shrink-0 mt-0.5" />}
              {item.type === "success" && <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />}

              <div className="flex-1">
                <p className="text-slate-800 dark:text-white/90 text-[11px] leading-snug font-medium">{item.text}</p>
                <span className="text-[9px] font-mono text-slate-400 dark:text-white/30 block mt-0.5">{item.time}</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
