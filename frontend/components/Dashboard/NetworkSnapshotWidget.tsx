"use client";

import React from "react";
import { Network, Users, ExternalLink, ShieldAlert, Sparkles } from "lucide-react";
import Link from "next/link";

export default function NetworkSnapshotWidget() {
  const topEntities = [
    { name: "Marcus Vance", role: "Kingpin Boss", risk: 96, syndicate: "Viper Syndicate" },
    { name: "Viktor Thorne", role: "Armed Commander", risk: 92, syndicate: "Apex Cartel" },
    { name: "Apex Logistics LLC", role: "Front Company", risk: 68, syndicate: "Viper Syndicate" },
  ];

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-md dark:shadow-xl space-y-4 flex flex-col justify-between transition-colors duration-300">
      <div>
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3.5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-500 border border-amber-500/20">
              <Network className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Network Topology Snapshot</h3>
              <p className="text-[11px] text-slate-500 dark:text-white/40 mt-0.5">Syndicate hierarchy & financial links</p>
            </div>
          </div>

          <Link
            href="/network-analysis"
            className="text-xs font-semibold text-amber-500 hover:underline flex items-center gap-1"
          >
            Full Canvas <ExternalLink className="h-3 w-3" />
          </Link>
        </div>

        {/* Graph Preview Cards */}
        <div className="mt-4 space-y-2.5">
          {topEntities.map((ent, idx) => (
            <div
              key={idx}
              className="p-3 rounded-2xl border border-slate-200/80 dark:border-white/[0.06] bg-slate-50/60 dark:bg-white/[0.02] flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-2.5">
                <div className="h-8 w-8 rounded-xl bg-amber-500/10 text-amber-500 border border-amber-500/20 font-bold font-mono flex items-center justify-center">
                  {ent.name.charAt(0)}
                </div>
                <div>
                  <h4 className="font-bold text-slate-900 dark:text-white text-xs">{ent.name}</h4>
                  <span className="text-[10px] text-slate-500 dark:text-white/40 block font-mono">{ent.role} • {ent.syndicate}</span>
                </div>
              </div>
              <span className="font-mono font-bold text-red-500 dark:text-red-400 text-[10px] bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/20">
                {ent.risk}% RISK
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-3 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between text-xs text-slate-500 dark:text-white/40 font-mono">
        <span className="flex items-center gap-1">
          <Users className="h-3.5 w-3.5 text-primary" /> 1,204 ENTITIES MAPPED
        </span>
        <span className="text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1">
          <Sparkles className="h-3 w-3" /> GNN ACTIVE
        </span>
      </div>
    </div>
  );
}
