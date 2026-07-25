"use client";

import React from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Activity, ShieldCheck, TrendingDown, Sparkles } from "lucide-react";
import { useTheme } from "@/components/Theme/ThemeProvider";

export interface HourlySimData {
  time: string;
  baseline: number;
  simulated: number;
}

export interface SectorImpactData {
  sector: string;
  before: number;
  after: number;
}

interface SimulationChartsProps {
  hourlyData: HourlySimData[];
  sectorData: SectorImpactData[];
}

export default function SimulationCharts({ hourlyData, sectorData }: SimulationChartsProps) {
  const { theme } = useTheme();
  const isDark = theme === "dark";
  const axisColor = isDark ? "rgba(255, 255, 255, 0.3)" : "rgba(100, 116, 139, 0.6)";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)";

  const CustomTooltip = ({
    active,
    payload,
    label,
  }: {
    active?: boolean;
    payload?: Array<{ value: number }>;
    label?: string;
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="p-3 rounded-xl bg-white dark:bg-[#0f172a]/95 border border-slate-200 dark:border-white/[0.12] shadow-xl backdrop-blur-xl text-xs space-y-1.5 font-mono">
          <p className="text-slate-400 dark:text-white/40 border-b border-slate-100 dark:border-white/[0.08] pb-1 font-bold">HORIZON: {label}</p>
          <div className="flex items-center justify-between gap-4 text-red-500 dark:text-red-400 font-bold">
            <span>Unmitigated Risk:</span>
            <span>{payload[0]?.value}</span>
          </div>
          <div className="flex items-center justify-between gap-4 text-emerald-600 dark:text-emerald-400 font-bold">
            <span>Simulated Outcome:</span>
            <span>{payload[1]?.value}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
      {/* 24-Hour Projected Incident Curve */}
      <div className="rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-sm dark:shadow-xl flex flex-col justify-between transition-colors duration-300">
        <div>
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" /> Projected Density Curve
            </h3>
            <span className="text-[10px] font-mono text-primary font-bold px-2 py-0.5 rounded bg-primary/10 border border-primary/20">
              MONTE CARLO v4.2
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-white/40 mt-1">
            24-hour incident trajectory comparison: Unmitigated baseline vs. Tactical patrol intervention.
          </p>
        </div>

        <div className="w-full h-[260px] mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={hourlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="simBaseline" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="simMitigated" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
              <XAxis dataKey="time" stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} fontFamily="monospace" />
              <YAxis stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} fontFamily="monospace" />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="baseline"
                stroke="#ef4444"
                fillOpacity={1}
                fill="url(#simBaseline)"
                strokeWidth={2}
                name="Unmitigated Risk"
              />
              <Area
                type="monotone"
                dataKey="simulated"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#simMitigated)"
                strokeWidth={2.5}
                name="Optimized Deployment"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="pt-3 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between text-xs text-slate-500 dark:text-white/50">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-red-500" /> Baseline</span>
            <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-emerald-500" /> Simulated</span>
          </div>
          <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1">
            <TrendingDown className="h-3 w-3" /> -38.4% RISK REDUCTION
          </span>
        </div>
      </div>

      {/* Sector Impact Distribution */}
      <div className="rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-sm dark:shadow-xl flex flex-col justify-between transition-colors duration-300">
        <div>
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-500 dark:text-emerald-400" /> Sector Risk Reduction Index
            </h3>
            <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-bold px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20">
              OPTIMIZED
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-white/40 mt-1">
            Comparative risk score reduction by geographical sector following patrol unit reallocation.
          </p>
        </div>

        <div className="w-full h-[260px] mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sectorData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
              <XAxis dataKey="sector" stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} fontFamily="monospace" />
              <YAxis stroke={axisColor} fontSize={10} tickLine={false} axisLine={false} fontFamily="monospace" />
              <Tooltip contentStyle={{ backgroundColor: isDark ? "#0f172a" : "#ffffff", borderColor: isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)", borderRadius: "12px" }} />
              <Bar dataKey="before" fill="#ef4444" radius={[4, 4, 0, 0]} name="Before Deployment" />
              <Bar dataKey="after" fill="#10b981" radius={[4, 4, 0, 0]} name="After Deployment" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="pt-3 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between text-xs text-slate-500 dark:text-white/50">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-red-500" /> Pre-Intervention</span>
            <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-emerald-500" /> Post-Intervention</span>
          </div>
          <span className="text-[10px] font-mono text-primary font-bold flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-accent" /> 4 SECTORS OPTIMIZED
          </span>
        </div>
      </div>
    </div>
  );
}
