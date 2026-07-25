"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  Download,
  Eye,
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  Plus,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import MetricCard from "@/components/Cards/MetricCard";
import PageHeader from "@/components/Common/PageHeader";
import StatusBadge from "@/components/Common/StatusBadge";
import ReportPreviewModal, { ReportItem } from "@/components/Reports/ReportPreviewModal";
import GenerateReportModal from "@/components/Reports/GenerateReportModal";

const initialReports: ReportItem[] = [
  {
    id: "REP-9041",
    title: "Downtown Commercial Bank Vault Intrusion & Explosive Heist",
    caseId: "CAS-8924",
    crimeType: "Armed Robbery",
    location: "Sector 4 - Downtown",
    officer: "Capt. Kamal Solanki",
    priority: "Critical",
    status: "Published",
    createdDate: "2026-07-24",
    summary: "High-priority intelligence synthesis regarding the Sector 4 commercial bank breach. Multi-modal surveillance analysis identifies Marcus 'Viper' Vance as lead suspect.",
  },
  {
    id: "REP-9040",
    title: "Port Harbor Narcotics Cargo Intercept & Wiretap Synthesis",
    caseId: "CAS-8923",
    crimeType: "Gang Activity",
    location: "Sector 2 - Port",
    officer: "Det. Maya Lin",
    priority: "High",
    status: "Under Review",
    createdDate: "2026-07-23",
    summary: "Cross-referenced encrypted comms and container manifest logs revealing illegal contraband distribution networks linked to Apex Logistics LLC.",
  },
  {
    id: "REP-9038",
    title: "Suburbs Coordinated Vehicle Theft Ring Investigation",
    caseId: "CAS-8921",
    crimeType: "Vehicle Theft",
    location: "Sector 3 - Suburbs",
    officer: "Off. Marcus Brody",
    priority: "Medium",
    status: "Published",
    createdDate: "2026-07-22",
    summary: "ANPR camera logs and chop-shop spatial heatmaps indicating systematic vehicle targeting across Sector 3 arterial roads.",
  },
  {
    id: "REP-9035",
    title: "Sector 1 Financial District Ransomware & Crypto Breach",
    caseId: "CAS-8918",
    crimeType: "Cybercrime",
    location: "Sector 1 - Commercial",
    officer: "Agent Krrish Yaduka",
    priority: "High",
    status: "Draft",
    createdDate: "2026-07-21",
    summary: "Cyber forensics report detailing ransomware payload signatures and crypto wallet trace originating from Shadow Syndicate servers.",
  },
  {
    id: "REP-9030",
    title: "Industrial Zone Armed Assault & Syndicate Rivalry Incident",
    caseId: "CAS-8915",
    crimeType: "Homicide",
    location: "Sector 5 - Industrial",
    officer: "Lt. James Miller",
    priority: "Critical",
    status: "Published",
    createdDate: "2026-07-20",
    summary: "Ballistics casing analysis and CCTV facial recognition confirming conflict between Viper Syndicate and Apex Cartel enforcers.",
  },
];

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportItem[]>(initialReports);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [priorityFilter, setPriorityFilter] = useState("All");

  const [previewReport, setPreviewReport] = useState<ReportItem | null>(null);
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleDownloadPdf = (report: ReportItem) => {
    const reportData = `SENTINEL AI - INTELLIGENCE DOSSIER REPORT\n=========================================\nREPORT ID: ${report.id}\nCASE ID: ${report.caseId}\nTITLE: ${report.title}\nLOCATION: ${report.location}\nCLASSIFICATION: ${report.crimeType}\nPRIORITY: ${report.priority}\nSTATUS: ${report.status}\nOFFICER: ${report.officer}\nDATE: ${report.createdDate}\n\nSUMMARY & EVIDENCE:\n${report.summary}\n\nCRYPTOGRAPHIC SIGNATURE: 0x89F4A92B4019E88092A1\nCJIS LEVEL 5 COMPLIANT AUDIT LOG VERIFIED\n`;
    const blob = new Blob([reportData], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${report.id}_Dossier.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showToast(`Intelligence Dossier ${report.id} downloaded.`);
  };

  const handleShare = (report: ReportItem) => {
    showToast(`Encrypted link generated for ${report.id}`);
  };

  const handleReportGenerated = (newReport: ReportItem) => {
    setReports([newReport, ...reports]);
    showToast(`New report ${newReport.id} successfully generated!`);
  };

  const filteredReports = reports.filter((r) => {
    if (statusFilter !== "All" && r.status !== statusFilter) return false;
    if (priorityFilter !== "All" && r.priority !== priorityFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = r.title.toLowerCase().includes(q);
      const matchCase = r.caseId.toLowerCase().includes(q);
      const matchOfficer = r.officer.toLowerCase().includes(q);
      if (!matchTitle && !matchCase && !matchOfficer) return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      <AnimatePresence>
        {toastMessage && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-20 right-6 z-50 px-4 py-2.5 rounded-2xl bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 text-xs font-bold font-mono shadow-2xl flex items-center gap-2 backdrop-blur-xl"
          >
            <CheckCircle2 className="h-4 w-4 text-emerald-500 dark:text-emerald-400" />
            {toastMessage}
          </motion.div>
        )}
      </AnimatePresence>

      <PageHeader
        title="Intelligence Reports Library"
        subtitle="Automated copilot synthesis documents, evidence summaries, and command dossiers."
        icon={FileText}
        statusBadge={<StatusBadge status={`${reports.length} DOSSIERS`} variant="info" />}
      >
        <button
          onClick={() => setIsGenerateModalOpen(true)}
          className="px-4 py-2 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white text-xs font-bold rounded-xl shadow-lg shadow-primary/20 flex items-center gap-2 transition-all"
        >
          <Plus className="h-4 w-4" /> Synthesize AI Report
        </button>
      </PageHeader>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Reports"
          value={reports.length}
          icon={FileText}
          trend="up"
          change="+12 this month"
          variant="primary"
        />
        <MetricCard
          title="Critical Dossiers"
          value={reports.filter((r) => r.priority === "Critical").length}
          icon={ShieldAlert}
          trend="up"
          change="Action Required"
          variant="danger"
        />
        <MetricCard
          title="Published Official"
          value={reports.filter((r) => r.status === "Published").length}
          icon={CheckCircle2}
          trend="neutral"
          change="Verified Hash"
          variant="success"
        />
        <MetricCard
          title="Copilot Synthesized"
          value="100%"
          icon={Sparkles}
          trend="up"
          change="v4.2 Model"
          variant="accent"
        />
      </div>

      {/* Filter Controls Bar */}
      <div className="p-4 rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4 shadow-sm dark:shadow-xl transition-colors duration-300">
        <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[300px]">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search reports by title, case ID, or officer..."
              className="w-full h-9 pl-9 pr-3 rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08] text-xs text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-white/30 focus:outline-none focus:border-primary/50 transition-all"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="h-9 px-3 rounded-xl bg-white dark:bg-[#050816] border border-slate-200 dark:border-white/[0.08] text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
          >
            <option value="All">All Statuses</option>
            <option value="Published">Published</option>
            <option value="Under Review">Under Review</option>
            <option value="Draft">Draft</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="h-9 px-3 rounded-xl bg-white dark:bg-[#050816] border border-slate-200 dark:border-white/[0.08] text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
          >
            <option value="All">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
          </select>
        </div>
      </div>

      {/* Reports Table Card */}
      <div className="rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-sm dark:shadow-xl overflow-hidden transition-colors duration-300">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-sans">
            <thead>
              <tr className="border-b border-slate-200 dark:border-white/[0.08] text-slate-400 dark:text-white/40 font-mono uppercase text-[10px]">
                <th className="py-3 px-3">Report ID</th>
                <th className="py-3 px-3">Dossier Title</th>
                <th className="py-3 px-3">Case ID</th>
                <th className="py-3 px-3">Location</th>
                <th className="py-3 px-3">Officer</th>
                <th className="py-3 px-3">Priority</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04]">
              {filteredReports.map((report) => (
                <tr key={report.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-colors group">
                  <td className="py-3.5 px-3 font-mono font-bold text-primary group-hover:underline">
                    {report.id}
                  </td>
                  <td className="py-3.5 px-3 font-bold text-slate-900 dark:text-white max-w-xs truncate">
                    {report.title}
                  </td>
                  <td className="py-3.5 px-3 font-mono text-slate-500 dark:text-white/60">{report.caseId}</td>
                  <td className="py-3.5 px-3 text-slate-500 dark:text-white/50">{report.location}</td>
                  <td className="py-3.5 px-3 text-slate-700 dark:text-white/70">{report.officer}</td>
                  <td className="py-3.5 px-3">
                    <span className={`px-2 py-0.5 rounded-full font-mono font-bold text-[10px] ${
                      report.priority === "Critical"
                        ? "bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20"
                        : report.priority === "High"
                        ? "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
                        : "bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20"
                    }`}>
                      {report.priority.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3.5 px-3">
                    <StatusBadge
                      status={report.status.toUpperCase()}
                      variant={report.status === "Published" ? "success" : report.status === "Under Review" ? "warning" : "neutral"}
                    />
                  </td>
                  <td className="py-3.5 px-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => setPreviewReport(report)}
                        className="p-1.5 rounded-lg bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/70 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-white/[0.08] transition-colors"
                        title="View Report"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDownloadPdf(report)}
                        className="p-1.5 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 transition-colors"
                        title="Download PDF"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modals */}
      <ReportPreviewModal
        report={previewReport}
        onClose={() => setPreviewReport(null)}
        onDownloadPdf={handleDownloadPdf}
        onShare={handleShare}
      />

      <GenerateReportModal
        isOpen={isGenerateModalOpen}
        onClose={() => setIsGenerateModalOpen(false)}
        onReportGenerated={handleReportGenerated}
      />
    </div>
  );
}
