"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  Activity,
  Sparkles,
  BellRing,
  Download,
  CheckCircle2,
  Sliders,
} from "lucide-react";
import Link from "next/link";

export default function QuickActionPanel() {
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const actions = [
    { label: "Generate AI Dossier", icon: FileText, href: "/reports", color: "from-primary to-blue-600" },
    { label: "Start Investigation", icon: Search, href: "/network-analysis", color: "from-purple-500 to-indigo-600" },
    { label: "Monte Carlo Run", icon: Activity, href: "/simulation", color: "from-amber-500 to-orange-600" },
    { label: "Trigger Threat Alert", icon: BellRing, href: "/alerts", color: "from-red-500 to-rose-600" },
  ];

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-md dark:shadow-xl space-y-4 transition-colors duration-300">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3.5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <Sliders className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-900 dark:text-white">Tactical Quick Actions</h3>
            <p className="text-[11px] text-slate-500 dark:text-white/40 mt-0.5">High-priority operational launchers</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2.5">
        {actions.map((act, idx) => {
          const Icon = act.icon;
          return (
            <Link
              key={idx}
              href={act.href}
              className={`p-3.5 rounded-2xl bg-gradient-to-br ${act.color} text-white font-bold text-xs flex flex-col justify-between h-24 shadow-lg hover:scale-[1.02] transition-all group relative overflow-hidden`}
            >
              <div className="flex items-center justify-between w-full">
                <Icon className="h-5 w-5 opacity-90 group-hover:scale-110 transition-transform" />
                <Sparkles className="h-3.5 w-3.5 opacity-60" />
              </div>
              <span className="text-xs font-bold leading-tight">{act.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
