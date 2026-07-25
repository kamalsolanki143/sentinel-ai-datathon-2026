"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus, LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
  icon?: LucideIcon;
  subtitle?: string;
  variant?: "default" | "primary" | "accent" | "danger" | "warning" | "success";
  status?: "critical" | "warning" | "neutral" | "success" | "normal" | "danger" | "primary" | "accent" | "default";
  sparklineData?: number[];
}

export default function MetricCard({
  title,
  value,
  change,
  trend = "neutral",
  icon: Icon,
  subtitle,
  variant = "default",
  status,
  sparklineData = [35, 45, 30, 60, 75, 50, 90],
}: MetricCardProps) {
  const getVariantStyles = () => {
    const effectiveVariant =
      variant !== "default"
        ? variant
        : status === "critical" || status === "danger"
        ? "danger"
        : status === "warning"
        ? "warning"
        : status === "success"
        ? "success"
        : status === "primary"
        ? "primary"
        : status === "accent"
        ? "accent"
        : "default";

    switch (effectiveVariant) {
      case "primary":
        return {
          glow: "hover:border-primary/40 hover:shadow-primary/10",
          iconBg: "bg-primary/10 text-primary border-primary/20",
        };
      case "accent":
        return {
          glow: "hover:border-accent/40 hover:shadow-accent/10",
          iconBg: "bg-accent/10 text-accent border-accent/20",
        };
      case "danger":
        return {
          glow: "hover:border-red-500/40 hover:shadow-red-500/10",
          iconBg: "bg-red-500/10 text-red-500 dark:text-red-400 border-red-500/20",
        };
      case "warning":
        return {
          glow: "hover:border-amber-500/40 hover:shadow-amber-500/10",
          iconBg: "bg-amber-500/10 text-amber-500 dark:text-amber-400 border-amber-500/20",
        };
      case "success":
        return {
          glow: "hover:border-emerald-500/40 hover:shadow-emerald-500/10",
          iconBg: "bg-emerald-500/10 text-emerald-500 dark:text-emerald-400 border-emerald-500/20",
        };
      default:
        return {
          glow: "hover:border-slate-300 dark:hover:border-white/20",
          iconBg: "bg-slate-100 dark:bg-white/[0.05] text-slate-600 dark:text-white/70 border-slate-200 dark:border-white/10",
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ duration: 0.2 }}
      className={`relative rounded-2xl bg-white/90 dark:bg-[#0f172a]/60 border border-slate-200/80 dark:border-white/[0.08] backdrop-blur-xl p-5 overflow-hidden shadow-sm dark:shadow-lg transition-all duration-300 ${styles.glow} group`}
    >
      {/* Background Cyber Grid Accent */}
      <div className="absolute inset-0 dot-grid opacity-30 pointer-events-none" />

      {/* Top Section */}
      <div className="flex items-start justify-between relative z-10">
        <div>
          <span className="text-[11px] font-semibold text-slate-500 dark:text-white/40 uppercase tracking-wider block mb-1">
            {title}
          </span>
          <div className="text-2xl lg:text-3xl font-bold tracking-tight text-slate-900 dark:text-white font-mono">
            {value}
          </div>
        </div>

        {Icon && (
          <div className={`p-2.5 rounded-xl border ${styles.iconBg} shadow-inner group-hover:scale-110 transition-transform`}>
            <Icon className="h-5 w-5" strokeWidth={2} />
          </div>
        )}
      </div>

      {/* Mini Sparkline & Footer */}
      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between relative z-10">
        <div className="flex items-center gap-1.5 text-xs font-medium">
          {change && (
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                trend === "up"
                  ? "bg-red-500/10 text-red-500 dark:text-red-400 border border-red-500/20"
                  : trend === "down"
                  ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                  : "bg-slate-100 dark:bg-white/[0.05] text-slate-600 dark:text-white/50 border border-slate-200 dark:border-white/10"
              }`}
            >
              {trend === "up" && <TrendingUp className="h-3 w-3" />}
              {trend === "down" && <TrendingDown className="h-3 w-3" />}
              {trend === "neutral" && <Minus className="h-3 w-3" />}
              {change}
            </span>
          )}
          {subtitle && <span className="text-[11px] text-slate-400 dark:text-white/30 truncate max-w-[120px]">{subtitle}</span>}
        </div>

        {/* CSS Sparkline Vector */}
        <div className="flex items-end gap-1 h-5">
          {sparklineData.map((val, idx) => (
            <div
              key={idx}
              className="w-1 bg-primary/30 group-hover:bg-primary rounded-t transition-all"
              style={{ height: `${(val / 100) * 100}%` }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
}
