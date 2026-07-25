"use client";

import React from "react";
import { X, ShieldAlert, Users, Network, FileText, ExternalLink, MapPin, Activity, AlertTriangle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { NetworkNode } from "./NetworkGraph";
import Link from "next/link";

interface EntityProfileModalProps {
  node: NetworkNode | null;
  onClose: () => void;
}

export default function EntityProfileModal({ node, onClose }: EntityProfileModalProps) {
  if (!node) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-end p-4 sm:p-6 bg-slate-900/50 dark:bg-[#050816]/70 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 50 }}
          className="w-full max-w-lg bg-white dark:bg-[#0f172a] border border-slate-200 dark:border-white/[0.12] rounded-3xl shadow-2xl p-6 space-y-6 overflow-y-auto max-h-[90vh]"
        >
          {/* Header */}
          <div className="flex items-start justify-between border-b border-slate-100 dark:border-white/[0.08] pb-4">
            <div className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-primary via-blue-500 to-accent text-white font-bold font-mono text-lg flex items-center justify-center shadow-md">
                {node.name.charAt(0)}
              </div>
              <div>
                <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-2">
                  {node.name}
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
                    ID: {node.id.toUpperCase()}
                  </span>
                </h3>
                <p className="text-xs text-slate-500 dark:text-white/40 font-mono">
                  {node.alias ? `ALIAS: "${node.alias}"` : "NO KNOWN ALIASES"} • {node.syndicate}
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-700 dark:text-white/40 dark:hover:text-white p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-white/10"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Risk Metrics Card */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.08] grid grid-cols-2 gap-4">
            <div>
              <span className="text-[10px] font-mono text-slate-400 dark:text-white/40 block">ASSESSED RISK SCORE</span>
              <span className="text-xl font-bold font-mono text-red-500 dark:text-red-400 flex items-center gap-1">
                {node.riskScore} / 100 <ShieldAlert className="h-4 w-4" />
              </span>
            </div>
            <div>
              <span className="text-[10px] font-mono text-slate-400 dark:text-white/40 block">ACTIVE WARRANTS</span>
              <span className="text-xl font-bold font-mono text-amber-500 flex items-center gap-1">
                {node.warrants} Outstanding <AlertTriangle className="h-4 w-4" />
              </span>
            </div>
          </div>

          {/* Role & Location Details */}
          <div className="space-y-2 text-xs font-sans">
            <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-white/[0.06]">
              <span className="text-slate-400 font-mono">PRIMARY ROLE</span>
              <span className="font-bold text-slate-900 dark:text-white">{node.role}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-white/[0.06]">
              <span className="text-slate-400 font-mono">LAST KNOWN LOCATION</span>
              <span className="font-bold text-slate-900 dark:text-white font-mono flex items-center gap-1">
                <MapPin className="h-3 w-3 text-primary" /> {node.lastLocation}
              </span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100 dark:border-white/[0.06]">
              <span className="text-slate-400 font-mono">NETWORK AFFILIATION</span>
              <span className="font-bold text-slate-900 dark:text-white">{node.syndicate}</span>
            </div>
          </div>

          {/* Known Associates */}
          <div className="space-y-3">
            <h4 className="font-bold text-xs text-slate-900 dark:text-white uppercase font-mono tracking-wider flex items-center gap-1.5">
              <Users className="h-4 w-4 text-primary" /> High-Confidence Associates
            </h4>
            <div className="grid grid-cols-2 gap-2 text-xs font-mono">
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/10">
                <span className="font-bold text-slate-900 dark:text-white block">Viktor Thorne</span>
                <span className="text-[10px] text-slate-400">Armed Enforcer</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/10">
                <span className="font-bold text-slate-900 dark:text-white block">Apex Logistics LLC</span>
                <span className="text-[10px] text-slate-400">Front Business</span>
              </div>
            </div>
          </div>

          {/* Action Footer */}
          <div className="pt-4 border-t border-slate-100 dark:border-white/[0.08] flex items-center justify-between">
            <Link
              href="/copilot"
              className="px-4 py-2.5 rounded-xl bg-primary text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-primary/20"
            >
              Analyze with Copilot <ExternalLink className="h-3.5 w-3.5" />
            </Link>
            <button
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 text-xs font-bold text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white"
            >
              Close Inspector
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
