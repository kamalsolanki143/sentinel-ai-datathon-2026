"use client";

import React from "react";
import Link from "next/link";
import { ShieldAlert, ArrowLeft, LayoutDashboard } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-[70vh] w-full flex flex-col items-center justify-center text-center space-y-6 px-4">
      <div className="p-4 rounded-3xl bg-red-500/10 border border-red-500/30 text-red-500 dark:text-red-400 shadow-2xl">
        <ShieldAlert className="h-12 w-12" />
      </div>

      <div className="space-y-2 max-w-md">
        <span className="text-xs font-mono font-bold text-red-500 dark:text-red-400 uppercase tracking-widest bg-red-500/10 px-3 py-1 rounded-full border border-red-500/20">
          ERROR 404 • ROUTE UNCLASSIFIED
        </span>
        <h1 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
          Sector Vector Not Found
        </h1>
        <p className="text-xs text-slate-500 dark:text-white/50 leading-relaxed">
          The requested command module or intelligence dossier location does not exist within Sentinel OS.
        </p>
      </div>

      <Link
        href="/dashboard"
        className="px-6 py-2.5 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary/20 flex items-center gap-2 transition-all"
      >
        <LayoutDashboard className="h-4 w-4" /> Return to Command Center
      </Link>
    </div>
  );
}
