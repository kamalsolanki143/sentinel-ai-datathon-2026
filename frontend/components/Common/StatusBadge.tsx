"use client";

import React from "react";

interface StatusBadgeProps {
  status?: string;
  children?: React.ReactNode;
  variant?: "success" | "warning" | "danger" | "critical" | "info" | "neutral";
  pulse?: boolean;
}

export default function StatusBadge({
  status,
  children,
  variant = "info",
  pulse = false,
}: StatusBadgeProps) {
  const getStyles = () => {
    switch (variant) {
      case "critical":
      case "danger":
        return "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/30 shadow-red-500/10";
      case "warning":
        return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30 shadow-amber-500/10";
      case "success":
        return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 shadow-emerald-500/10";
      case "neutral":
        return "bg-slate-100 dark:bg-white/[0.05] text-slate-600 dark:text-white/50 border-slate-200 dark:border-white/10";
      case "info":
      default:
        return "bg-primary/10 text-primary border-primary/30 shadow-primary/10";
    }
  };

  const getPulseColor = () => {
    switch (variant) {
      case "critical":
      case "danger":
        return "bg-red-500 dark:bg-red-400";
      case "warning":
        return "bg-amber-500 dark:bg-amber-400";
      case "success":
        return "bg-emerald-500 dark:bg-emerald-400";
      default:
        return "bg-primary";
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider uppercase border shadow-sm ${getStyles()}`}
    >
      {pulse && (
        <span className="relative flex h-1.5 w-1.5">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${getPulseColor()}`} />
          <span className={`relative inline-flex rounded-full h-1.5 w-1.5 ${getPulseColor()}`} />
        </span>
      )}
      {children || status}
    </span>
  );
}
