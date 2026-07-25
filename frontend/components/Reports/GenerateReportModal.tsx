"use client";

import React, { useState } from "react";
import { X, Sparkles, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ReportItem } from "./ReportPreviewModal";

interface GenerateReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onReportGenerated: (newReport: ReportItem) => void;
}

export default function GenerateReportModal({
  isOpen,
  onClose,
  onReportGenerated,
}: GenerateReportModalProps) {
  const [caseId, setCaseId] = useState("CAS-8924");
  const [title, setTitle] = useState("Downtown Syndicate Commercial Vault Intrusion");
  const [crimeType, setCrimeType] = useState("Armed Robbery");
  const [location, setLocation] = useState("Sector 4 - Downtown");
  const [priority, setPriority] = useState<"Critical" | "High" | "Medium" | "Low">("Critical");
  const [officer, setOfficer] = useState("Agent Sarah Connor");
  const [includeCopilot, setIncludeCopilot] = useState(true);
  const [includeNetwork, setIncludeNetwork] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    setTimeout(() => {
      setIsGenerating(false);
      const generated: ReportItem = {
        id: `REP-${Math.floor(1000 + Math.random() * 9000)}`,
        title: title || "Automated AI Intelligence Synthesis",
        caseId,
        crimeType,
        location,
        officer,
        priority,
        status: "Published",
        createdDate: new Date().toISOString().split("T")[0],
        summary: `Synthesized intelligence report compiling AI Copilot graph findings and real-time surveillance vectors for case ${caseId}. Includes spatial risk predictions, evidence links, and recommended patrol vector enforcement for ${location}.`,
      };
      onReportGenerated(generated);
      onClose();
    }, 1500);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-[#050816]/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 15 }}
          className="bg-white dark:bg-[#0f172a]/95 border border-slate-200 dark:border-white/[0.12] w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden z-10"
        >
          {/* Header */}
          <div className="p-4 border-b border-slate-100 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.02] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-accent/10 text-accent border border-accent/20">
                <Sparkles className="h-4 w-4" />
              </div>
              <div>
                <h2 className="font-bold text-sm text-slate-900 dark:text-white">Generate AI Intelligence Report</h2>
                <p className="text-[11px] text-slate-500 dark:text-white/40">Synthesize copilot data & network telemetry</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-700 dark:text-white/40 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-white/[0.06] transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleGenerate} className="p-5 space-y-4 text-xs">
            <div>
              <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                Report Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.03] px-3 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-white/20 focus:outline-none focus:border-primary/50 transition-all"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Case Identifier
                </label>
                <input
                  type="text"
                  value={caseId}
                  onChange={(e) => setCaseId(e.target.value)}
                  required
                  className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.03] px-3 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all font-mono"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Crime Classification
                </label>
                <select
                  value={crimeType}
                  onChange={(e) => setCrimeType(e.target.value)}
                  className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-[#050816] px-3 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                >
                  <option value="Armed Robbery">Armed Robbery</option>
                  <option value="Narcotics Trafficking">Narcotics Trafficking</option>
                  <option value="Cybercrime">Cybercrime</option>
                  <option value="Financial Fraud">Financial Fraud</option>
                  <option value="Homicide">Homicide</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Target Sector
                </label>
                <select
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-[#050816] px-3 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                >
                  <option value="Sector 1 - Commercial">Sector 1 - Commercial</option>
                  <option value="Sector 2 - Port & Harbor">Sector 2 - Port & Harbor</option>
                  <option value="Sector 3 - Suburbs">Sector 3 - Suburbs</option>
                  <option value="Sector 4 - Downtown">Sector 4 - Downtown</option>
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Priority Rating
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as "Critical" | "High" | "Medium" | "Low")}
                  className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-[#050816] px-3 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                >
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            </div>

            {/* AI Synthesizer Options */}
            <div className="p-3.5 rounded-xl border border-slate-200 dark:border-white/[0.06] bg-slate-50 dark:bg-white/[0.02] space-y-2.5">
              <span className="text-[10px] font-bold text-slate-400 dark:text-white/40 uppercase tracking-widest block">
                Security Copilot Intelligence Modules
              </span>
              <div className="space-y-2">
                <label className="flex items-center gap-2.5 text-slate-700 dark:text-white/70 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeCopilot}
                    onChange={(e) => setIncludeCopilot(e.target.checked)}
                    className="rounded border-slate-300 dark:border-white/20 bg-white dark:bg-white/5 text-primary focus:ring-primary/40 h-4 w-4"
                  />
                  <span>Inject Copilot Spatial Threat Analytics & Risk Curves</span>
                </label>
                <label className="flex items-center gap-2.5 text-slate-700 dark:text-white/70 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeNetwork}
                    onChange={(e) => setIncludeNetwork(e.target.checked)}
                    className="rounded border-slate-300 dark:border-white/20 bg-white dark:bg-white/5 text-primary focus:ring-primary/40 h-4 w-4"
                  />
                  <span>Inject Criminal Syndicate Node Linkage Data</span>
                </label>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-3 border-t border-slate-100 dark:border-white/[0.08] flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white rounded-xl font-semibold transition-all"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isGenerating}
                className="px-5 py-2 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold rounded-xl shadow-lg shadow-primary/20 flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin text-white" />
                    <span>Synthesizing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    <span>Synthesize Report</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
