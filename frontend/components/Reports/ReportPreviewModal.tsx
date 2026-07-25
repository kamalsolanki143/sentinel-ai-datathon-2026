"use client";

import React, { useState } from "react";
import {
  X,
  Download,
  Share2,
  ShieldAlert,
  FileCheck,
  Check,
  FileText,
  Sparkles,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface ReportItem {
  id: string;
  title: string;
  caseId: string;
  crimeType: string;
  location: string;
  officer: string;
  priority: "Critical" | "High" | "Medium" | "Low";
  status: "Published" | "Under Review" | "Draft" | "Archived";
  createdDate: string;
  summary: string;
}

interface ReportPreviewModalProps {
  report: ReportItem | null;
  onClose: () => void;
  onDownloadPdf: (report: ReportItem) => void;
  onShare: (report: ReportItem) => void;
}

export default function ReportPreviewModal({
  report,
  onClose,
  onDownloadPdf,
  onShare,
}: ReportPreviewModalProps) {
  const [copied, setCopied] = useState(false);

  if (!report) return null;

  const handleShareClick = () => {
    onShare(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-[#050816]/80 backdrop-blur-md overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 15 }}
          className="bg-white dark:bg-[#0f172a]/95 border border-slate-200 dark:border-white/[0.12] w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] z-10"
        >
          {/* Header Bar */}
          <div className="p-4 border-b border-slate-100 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.02] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
                <FileText className="h-4 w-4" />
              </div>
              <div>
                <h2 className="font-bold text-sm text-slate-900 dark:text-white">Intelligence Synthesis Document</h2>
                <span className="text-[10px] font-mono text-slate-400 dark:text-white/40">ID: {report.id} • {report.caseId}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => onDownloadPdf(report)}
                className="px-3 py-1.5 bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all shadow-lg shadow-primary/20"
              >
                <Download className="h-3.5 w-3.5" /> Export PDF
              </button>
              <button
                onClick={handleShareClick}
                className="p-2 bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/70 hover:text-slate-900 dark:hover:text-white rounded-xl text-xs font-semibold border border-slate-200 dark:border-white/[0.08] transition-all"
                title="Share Link"
              >
                {copied ? <Check className="h-4 w-4 text-emerald-500 dark:text-emerald-400" /> : <Share2 className="h-4 w-4" />}
              </button>
              <button
                onClick={onClose}
                className="p-2 text-slate-400 hover:text-slate-700 dark:text-white/40 dark:hover:text-white rounded-xl hover:bg-slate-100 dark:hover:bg-white/[0.06] transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Document Content - Intelligence Document Style */}
          <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6 bg-slate-50 dark:bg-[#080d1a] text-slate-900 dark:text-slate-100 font-sans selection:bg-primary selection:text-white relative">
            {/* Classification Header */}
            <div className="border border-red-500/30 bg-red-500/10 p-3 rounded-xl flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-red-600 dark:text-red-400 font-mono font-bold tracking-widest uppercase">
                <ShieldAlert className="h-4 w-4" />
                TOP SECRET // LAW ENFORCEMENT SENSITIVE
              </div>
              <span className="font-mono text-[10px] text-slate-500 dark:text-white/40">CLASSIFICATION: LEVEL 5</span>
            </div>

            {/* Document Title Block */}
            <div className="border-b border-slate-200 dark:border-white/[0.08] pb-6 space-y-3">
              <span className="text-[10px] font-mono font-bold text-primary uppercase tracking-[0.2em] block">
                SENTINEL SECURITY COPILOT v4.2 DOSSIER
              </span>
              <h1 className="text-xl md:text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                {report.title}
              </h1>
              <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-500 dark:text-white/50 pt-1">
                <span>CASE: <strong className="text-slate-900 dark:text-white">{report.caseId}</strong></span>
                <span>OFFICER: <strong className="text-slate-900 dark:text-white">{report.officer}</strong></span>
                <span>DATE: <strong className="text-slate-900 dark:text-white">{report.createdDate}</strong></span>
              </div>
            </div>

            {/* Metadata Summary Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-xl bg-white dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] text-xs font-mono">
              <div>
                <span className="text-slate-400 dark:text-white/40 block text-[10px]">CRIME TYPE</span>
                <span className="text-slate-900 dark:text-white font-bold">{report.crimeType}</span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-white/40 block text-[10px]">TARGET SECTOR</span>
                <span className="text-slate-900 dark:text-white font-bold">{report.location}</span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-white/40 block text-[10px]">PRIORITY</span>
                <span className="text-red-500 dark:text-red-400 font-bold">{report.priority}</span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-white/40 block text-[10px]">STATUS</span>
                <span className="text-emerald-600 dark:text-emerald-400 font-bold">{report.status}</span>
              </div>
            </div>

            {/* Executive Summary */}
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <Sparkles className="h-3.5 w-3.5 text-accent" /> Executive Threat Synthesis
              </h3>
              <p className="text-xs md:text-sm text-slate-700 dark:text-white/80 leading-relaxed bg-white dark:bg-white/[0.01] p-4 rounded-xl border border-slate-200 dark:border-white/[0.04]">
                {report.summary}
              </p>
            </div>

            {/* Cryptographic Sign-Off Block */}
            <div className="pt-6 border-t border-slate-200 dark:border-white/[0.08] flex items-center justify-between text-xs font-mono text-slate-500 dark:text-white/40">
              <div className="flex items-center gap-2">
                <FileCheck className="h-4 w-4 text-emerald-500 dark:text-emerald-400" />
                <span>CRYPTOGRAPHIC HASH: 0x89f4...3a91 VERIFIED</span>
              </div>
              <span>ISSUED BY SENTINEL OS</span>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
