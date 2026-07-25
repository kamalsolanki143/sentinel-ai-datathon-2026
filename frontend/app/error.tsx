"use client";

import React, { useEffect } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Sentinel System Error Captured:", error);
  }, [error]);

  return (
    <div className="min-h-[calc(100vh-56px)] w-full flex flex-col items-center justify-center p-6 text-center">
      <div className="h-16 w-16 bg-red-500/10 text-red-500 rounded-2xl flex items-center justify-center mb-6 border border-red-500/20 shadow-lg shadow-red-500/10">
        <AlertTriangle className="h-8 w-8" />
      </div>

      <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">System Subsystem Fault Detected</h2>
      <p className="text-sm text-slate-500 dark:text-white/50 max-w-md mb-8">
        An unexpected error occurred in the intelligence interface. Telemetry anomaly has been logged automatically.
      </p>

      <button
        onClick={() => reset()}
        className="px-6 py-2.5 bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/70 hover:text-slate-900 dark:hover:text-white rounded-xl border border-slate-200 dark:border-white/[0.1] transition-all flex items-center gap-2 text-sm font-medium shadow-sm"
      >
        <RotateCcw className="h-4 w-4 text-primary" />
        Restart Intelligence Subsystem
      </button>
    </div>
  );
}
