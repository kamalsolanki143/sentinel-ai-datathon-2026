"use client";

import React, { useState } from "react";
import {
  BrainCircuit,
  Sparkles,
  AlertOctagon,
  ShieldAlert,
  ChevronRight,
  TrendingUp,
  MapPin,
  ExternalLink,
  CheckCircle2,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

interface InsightCard {
  id: string;
  title: string;
  category: "Pattern" | "Hotspot" | "Suspicious" | "Recommendation";
  confidence: number;
  priority: "Critical" | "High" | "Medium";
  description: string;
  location: string;
  time: string;
}

const mockInsights: InsightCard[] = [
  {
    id: "INS-101",
    title: "Syndicate Getaway Corridor Shift Detected",
    category: "Pattern",
    confidence: 96,
    priority: "Critical",
    description: "ANPR telemetry indicates Marcus Vance's logistics network has shifted getaway transit from Highway 101 to Sector 4 Industrial Corridor.",
    location: "Sector 4 Industrial",
    time: "4m ago",
  },
  {
    id: "INS-102",
    title: "Emerging Hotspot: Port Contraband Terminal 3",
    category: "Hotspot",
    confidence: 92,
    priority: "High",
    description: "Thermal drone feeds and wiretap intercepts confirm an 88% probability of illegal cargo transfer between 22:00 and 02:00 EST.",
    location: "Sector 2 Port Gate 4",
    time: "14m ago",
  },
  {
    id: "INS-103",
    title: "Recommended Action: Deploy Unit Alpha-4 to Bank Vault",
    category: "Recommendation",
    confidence: 98,
    priority: "Critical",
    description: "Security Copilot recommends pre-positioning Strike Unit Alpha-4 at Downtown Bank Vault perimeter to achieve -42% incident reduction.",
    location: "Sector 4 Downtown",
    time: "28m ago",
  },
];

export default function AIInsightsFeed() {
  const [insights, setInsights] = useState<InsightCard[]>(mockInsights);
  const [dismissedIds, setDismissedIds] = useState<string[]>([]);

  const handleDismiss = (id: string) => {
    setDismissedIds((prev) => [...prev, id]);
  };

  const activeInsights = insights.filter((i) => !dismissedIds.includes(i.id));

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-md dark:shadow-xl space-y-4 transition-colors duration-300">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3.5">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-accent/10 text-accent border border-accent/20">
            <BrainCircuit className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
              Security Copilot AI Insights
              <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-accent/20 text-accent border border-accent/30">
                LIVE NEURAL FEED
              </span>
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-white/40 mt-0.5">
              Automated pattern detection, hotspot alerts, and tactical recommendations
            </p>
          </div>
        </div>

        <Link
          href="/copilot"
          className="text-xs font-semibold text-accent hover:text-accent/80 flex items-center gap-1 transition-colors"
        >
          Open Copilot <ChevronRight className="h-3.5 w-3.5" />
        </Link>
      </div>

      {/* Insights Cards List */}
      <div className="space-y-3">
        <AnimatePresence>
          {activeInsights.map((insight) => (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={`p-4 rounded-2xl border transition-all space-y-3 relative group ${
                insight.priority === "Critical"
                  ? "border-red-500/30 bg-red-500/5 hover:border-red-500/50"
                  : "border-slate-200/80 dark:border-white/[0.08] bg-slate-50/60 dark:bg-white/[0.02] hover:border-slate-300 dark:hover:border-white/20"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded-full font-mono font-bold text-[10px] ${
                    insight.priority === "Critical"
                      ? "bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20"
                      : "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
                  }`}>
                    {insight.priority.toUpperCase()}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400 dark:text-white/40">
                    {insight.category.toUpperCase()} • {insight.time}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    {insight.confidence}% CONFIDENCE
                  </span>
                  <button
                    onClick={() => handleDismiss(insight.id)}
                    className="text-slate-400 hover:text-slate-700 dark:text-white/30 dark:hover:text-white text-[10px] font-mono p-1"
                  >
                    Dismiss
                  </button>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-xs text-slate-900 dark:text-white">{insight.title}</h4>
                <p className="text-xs text-slate-600 dark:text-white/70 mt-1 leading-relaxed">{insight.description}</p>
              </div>

              <div className="pt-2 border-t border-slate-200/60 dark:border-white/[0.06] flex items-center justify-between text-[11px] text-slate-500 dark:text-white/40 font-mono">
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3 text-primary" /> {insight.location}
                </span>

                <Link
                  href="/copilot"
                  className="text-primary hover:underline flex items-center gap-1 font-semibold"
                >
                  Analyze with Copilot <ExternalLink className="h-3 w-3" />
                </Link>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {activeInsights.length === 0 && (
          <div className="p-6 text-center text-xs text-slate-400 dark:text-white/40 font-mono border border-dashed border-slate-200 dark:border-white/10 rounded-2xl">
            ALL AI INSIGHTS ACKNOWLEDGED BY COMMANDER
          </div>
        )}
      </div>
    </div>
  );
}
