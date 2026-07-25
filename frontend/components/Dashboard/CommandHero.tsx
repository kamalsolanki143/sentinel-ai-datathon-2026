"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  MapPin,
  Clock,
  Sparkles,
  Radio,
  Activity,
  Zap,
  TrendingDown,
  Navigation,
  ShieldCheck,
} from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";

export default function CommandHero() {
  const [currentTime, setCurrentTime] = useState("");
  const [greeting, setGreeting] = useState("Good Morning");

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }));

      const hour = now.getHours();
      if (hour < 12) setGreeting("Good Morning");
      else if (hour < 18) setGreeting("Good Afternoon");
      else setGreeting("Good Evening");
    };

    updateClock();
    const timer = setInterval(updateClock, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.1] bg-gradient-to-r from-white via-slate-50 to-blue-50/40 dark:from-[#0f172a]/90 dark:via-[#0b1329]/90 dark:to-[#081024]/90 backdrop-blur-2xl p-6 lg:p-8 shadow-md dark:shadow-2xl relative overflow-hidden transition-colors duration-300">
      {/* Background Cyber Grid Accent */}
      <div className="absolute inset-0 cyber-grid opacity-15 dark:opacity-25 pointer-events-none" />

      {/* Top Banner Row */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
        {/* Left Welcome Header */}
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <span className="px-3 py-1 rounded-full bg-primary/10 text-primary border border-primary/20 font-bold flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-accent animate-pulse" />
              SENTINEL CORE OPERATIONAL
            </span>
            <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-bold flex items-center gap-1.5">
              <Radio className="h-3.5 w-3.5 text-emerald-500 animate-ping" />
              DEFCON 3 • ELEVATED
            </span>
          </div>

          <div className="space-y-1">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              {greeting}, <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-500 to-accent">Commander Solanki</span>
            </h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-white/50 max-w-xl">
              Downtown Sector 4 under active spatial monitoring. Security Copilot has detected 3 high-probability incident clusters.
            </p>
          </div>
        </div>

        {/* Right Status Panel */}
        <div className="flex flex-wrap items-center gap-3 shrink-0">
          <div className="p-3.5 rounded-2xl bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] text-xs font-mono space-y-1 shadow-sm">
            <div className="flex items-center gap-2 text-slate-400 dark:text-white/40 text-[10px]">
              <MapPin className="h-3.5 w-3.5 text-primary" /> JURISDICTION
            </div>
            <div className="font-bold text-slate-900 dark:text-white">Metropolitan Sector 4</div>
          </div>

          <div className="p-3.5 rounded-2xl bg-white dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.08] text-xs font-mono space-y-1 shadow-sm">
            <div className="flex items-center gap-2 text-slate-400 dark:text-white/40 text-[10px]">
              <Clock className="h-3.5 w-3.5 text-accent" /> SYSTEM TIME
            </div>
            <div className="font-bold text-primary">{currentTime || "10:42:00 EST"}</div>
          </div>

          <Link
            href="/copilot"
            className="px-5 py-3.5 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-2xl shadow-xl shadow-primary/25 flex items-center gap-2 transition-all hover:scale-105"
          >
            <Sparkles className="h-4 w-4" /> Ask Security Copilot
          </Link>
        </div>
      </div>

      {/* Bottom Summary Bar */}
      <div className="mt-6 pt-5 border-t border-slate-200/80 dark:border-white/[0.08] grid grid-cols-2 sm:grid-cols-4 gap-4 relative z-10 text-xs font-mono">
        <div className="flex items-center gap-3 p-2.5 rounded-xl bg-white/60 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.04]">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-white/40 block">MODEL PRECISION</span>
            <span className="font-bold text-slate-900 dark:text-white">99.8% PRECISION</span>
          </div>
        </div>

        <div className="flex items-center gap-3 p-2.5 rounded-xl bg-white/60 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.04]">
          <div className="p-2 rounded-lg bg-primary/10 text-primary">
            <Activity className="h-4 w-4" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-white/40 block">ACTIVE PATROLS</span>
            <span className="font-bold text-slate-900 dark:text-white">845 / 900 UNITS</span>
          </div>
        </div>

        <div className="flex items-center gap-3 p-2.5 rounded-xl bg-white/60 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.04]">
          <div className="p-2 rounded-lg bg-accent/10 text-accent">
            <Zap className="h-4 w-4" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-white/40 block">RESPONSE TIME</span>
            <span className="font-bold text-accent">&lt; 2.4 MINUTES</span>
          </div>
        </div>

        <div className="flex items-center gap-3 p-2.5 rounded-xl bg-white/60 dark:bg-white/[0.02] border border-slate-200/60 dark:border-white/[0.04]">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-500">
            <TrendingDown className="h-4 w-4" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 dark:text-white/40 block">PREDICTED RISK</span>
            <span className="font-bold text-emerald-600 dark:text-emerald-400">-42.5% REDUCTION</span>
          </div>
        </div>
      </div>
    </div>
  );
}
