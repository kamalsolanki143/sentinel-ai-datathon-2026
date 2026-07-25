"use client";

import React from "react";
import { Activity } from "lucide-react";

export default function Loading() {
  return (
    <div className="min-h-[60vh] w-full flex flex-col items-center justify-center space-y-4">
      <div className="p-4 rounded-2xl bg-primary/10 border border-primary/20 text-primary animate-bounce shadow-xl shadow-primary/20">
        <Activity className="h-8 w-8 animate-spin" />
      </div>
      <div className="text-center font-mono space-y-1">
        <p className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
          SYNCHRONIZING SENTINEL TELEMETRY...
        </p>
        <p className="text-xs text-slate-500 dark:text-white/40">
          Decrypting neural copilot weights & spatial threat maps
        </p>
      </div>
    </div>
  );
}
