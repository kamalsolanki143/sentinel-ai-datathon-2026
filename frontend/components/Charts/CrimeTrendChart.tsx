"use client";

import React, { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Activity, Sparkles } from "lucide-react";
import { useTheme } from "@/components/Theme/ThemeProvider";

interface DataPoint {
  time: string;
  incidents: number;
  predicted: number;
  resolved: number;
}

const mockTrendData: DataPoint[] = [
  { time: "00:00", incidents: 12, predicted: 14, resolved: 8 },
  { time: "03:00", incidents: 18, predicted: 22, resolved: 15 },
  { time: "06:00", incidents: 8, predicted: 10, resolved: 6 },
  { time: "09:00", incidents: 25, predicted: 28, resolved: 20 },
  { time: "12:00", incidents: 42, predicted: 40, resolved: 32 },
  { time: "15:00", incidents: 55, predicted: 50, resolved: 45 },
  { time: "18:00", incidents: 68, predicted: 72, resolved: 52 },
  { time: "21:00", incidents: 84, predicted: 90, resolved: 60 },
];

export default function CrimeTrendChart() {
  const { theme } = useTheme();
  const [timeframe, setTimeframe] = useState<"24h" | "7d" | "30d">("24h");

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
        <div className="p-3 rounded-xl bg-white dark:bg-[#0f172a]/95 border border-slate-200 dark:border-white/[0.12] shadow-2xl backdrop-blur-xl text-xs space-y-1.5">
          <p className="font-mono font-bold text-slate-500 dark:text-white/50 border-b border-slate-100 dark:border-white/[0.08] pb-1">
            TIMESTAMP: {label}
          </p>
          <div className="flex items-center justify-between gap-4 text-red-500 dark:text-red-400 font-semibold">
            <span>Detected Incidents:</span>
            <span className="font-mono font-bold">{payload[0]?.value}</span>
          </div>
          {payload[1] && (
            <div className="flex items-center justify-between gap-4 text-primary font-semibold">
              <span>AI Predicted Threshold:</span>
              <span className="font-mono font-bold">{payload[1]?.value}</span>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  const isDark = theme === "dark";
  const axisColor = isDark ? "rgba(255, 255, 255, 0.3)" : "rgba(100, 116, 139, 0.6)";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.05)" : "rgba(0, 0, 0, 0.05)";

  return (
    <div className="rounded-2xl bg-white/90 dark:bg-[#0f172a]/60 border border-slate-200/80 dark:border-white/[0.08] backdrop-blur-xl p-5 shadow-sm dark:shadow-xl flex flex-col justify-between space-y-4 transition-colors duration-300">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
            <Activity className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-wide">
              Temporal Crime Threat Analytics
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-white/40">
              Real-time incident velocity vs Security Copilot predictive baseline
            </p>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          <div className="flex p-1 rounded-xl bg-slate-100 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08] text-[11px]">
            {(["24h", "7d", "30d"] as const).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-2.5 py-1 rounded-lg font-mono font-bold transition-all ${
                  timeframe === tf
                    ? "bg-primary text-white shadow"
                    : "text-slate-500 dark:text-white/40 hover:text-slate-900 dark:hover:text-white"
                }`}
              >
                {tf.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-64 w-full pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={mockTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorIncidents" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} vertical={false} />
            <XAxis
              dataKey="time"
              stroke={axisColor}
              fontSize={10}
              tickLine={false}
              axisLine={false}
              fontFamily="monospace"
            />
            <YAxis
              stroke={axisColor}
              fontSize={10}
              tickLine={false}
              axisLine={false}
              fontFamily="monospace"
            />
            <Tooltip content={<CustomTooltip />} />

            <Area
              type="monotone"
              dataKey="incidents"
              stroke="#ef4444"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#colorIncidents)"
            />
            <Area
              type="monotone"
              dataKey="predicted"
              stroke="#3b82f6"
              strokeWidth={2}
              strokeDasharray="4 4"
              fillOpacity={1}
              fill="url(#colorPredicted)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Legend & Stats */}
      <div className="pt-3 border-t border-slate-100 dark:border-white/[0.06] flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-red-500" />
            <span className="text-slate-600 dark:text-white/60">Actual Incidents</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-primary" />
            <span className="text-slate-600 dark:text-white/60">AI Predicted Model</span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-white/40 font-mono">
          <Sparkles className="h-3 w-3 text-accent" />
          <span>CONFIDENCE SCORE: 94.8%</span>
        </div>
      </div>
    </div>
  );
}
