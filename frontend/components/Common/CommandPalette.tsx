"use client";

import React, { useState, useEffect } from "react";
import {
  Search,
  LayoutDashboard,
  BrainCircuit,
  Network,
  Activity,
  FileText,
  BellRing,
  Settings,
  ShieldAlert,
  ArrowRight,
  Sparkles,
  X,
  MapPin,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const quickLinks = [
    { title: "Dashboard Overview", desc: "Live crime intelligence metrics & spatial map", href: "/dashboard", icon: LayoutDashboard, category: "Navigation" },
    { title: "Security Copilot", desc: "Ask AI intelligence questions & analyze evidence", href: "/copilot", icon: BrainCircuit, category: "AI & Intelligence" },
    { title: "Network Intel Graph", desc: "Syndicate node graph & link analysis", href: "/network-analysis", icon: Network, category: "Investigative" },
    { title: "Threat Simulation", desc: "Monte Carlo crime prediction & patrol optimizer", href: "/simulation", icon: Activity, category: "Analytics" },
    { title: "Generated Reports", desc: "Official intelligence documentation library", href: "/reports", icon: FileText, category: "Documentation" },
    { title: "Active Alerts", desc: "Real-time threat feeds & high priority notifications", href: "/alerts", icon: BellRing, category: "Threat Response" },
    { title: "System Settings", desc: "API configurations, models & security roles", href: "/settings", icon: Settings, category: "System" },
  ];

  const quickCases = [
    { title: "CAS-8924 - Downtown Vault Intrusion", status: "Critical", location: "Sector 4 - Downtown", href: "/copilot" },
    { title: "CAS-9102 - Harbor Narcotics Smuggling", status: "High", location: "Sector 2 - Port & Harbor", href: "/network-analysis" },
    { title: "CAS-7731 - Cyber Identity Theft Ring", status: "Medium", location: "Sector 1 - Commercial", href: "/reports" },
  ];

  const filteredLinks = quickLinks.filter(
    (item) =>
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.desc.toLowerCase().includes(query.toLowerCase()) ||
      item.category.toLowerCase().includes(query.toLowerCase())
  );

  const filteredCases = quickCases.filter(
    (item) =>
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.location.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (href: string) => {
    router.push(href);
    onClose();
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 sm:px-6">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-slate-900/60 dark:bg-[#050816]/80 backdrop-blur-md"
        />

        {/* Modal Dialog */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: -10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: -10 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="relative w-full max-w-2xl rounded-2xl bg-white dark:bg-[#0f172a]/95 border border-slate-200 dark:border-white/[0.12] shadow-2xl overflow-hidden z-10"
        >
          {/* Header Input */}
          <div className="flex items-center px-4 border-b border-slate-100 dark:border-white/[0.08] bg-slate-50/50 dark:bg-white/[0.02]">
            <Search className="h-4 w-4 text-primary shrink-0 mr-3" />
            <input
              type="text"
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type a command, suspect name, or search modules..."
              className="w-full py-4 text-sm text-slate-900 dark:text-white bg-transparent outline-none placeholder:text-slate-400 dark:placeholder:text-white/30"
            />
            {query && (
              <button onClick={() => setQuery("")} className="text-slate-400 hover:text-slate-700 dark:text-white/30 dark:hover:text-white/70 p-1">
                <X className="h-4 w-4" />
              </button>
            )}
            <kbd className="hidden sm:inline-flex items-center gap-1 ml-3 px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 dark:bg-white/[0.06] border border-slate-200 dark:border-white/[0.08] text-slate-500 dark:text-white/40">
              ESC
            </kbd>
          </div>

          {/* Results Area */}
          <div className="max-h-[380px] overflow-y-auto p-3 space-y-4 no-scrollbar">
            {/* Quick Modules */}
            <div>
              <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400 dark:text-white/30 flex items-center justify-between">
                <span>Modules & Operations</span>
                <span className="text-primary/70">{filteredLinks.length} available</span>
              </div>
              <div className="mt-1 space-y-1">
                {filteredLinks.map((item) => (
                  <button
                    key={item.href}
                    onClick={() => handleSelect(item.href)}
                    className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-white/[0.05] border border-transparent hover:border-slate-200 dark:hover:border-white/[0.06] transition-all group text-left"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10 text-primary border border-primary/20 group-hover:bg-primary group-hover:text-white transition-colors">
                        <item.icon className="h-4 w-4" />
                      </div>
                      <div>
                        <h4 className="text-xs font-semibold text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                          {item.title}
                        </h4>
                        <p className="text-[11px] text-slate-500 dark:text-white/40">{item.desc}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[9px] uppercase font-mono px-2 py-0.5 rounded bg-slate-100 dark:bg-white/[0.04] text-slate-500 dark:text-white/30 border border-slate-200 dark:border-white/[0.06]">
                        {item.category}
                      </span>
                      <ArrowRight className="h-3.5 w-3.5 text-slate-300 dark:text-white/20 group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Recent Cases */}
            <div>
              <div className="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400 dark:text-white/30">
                Active Intelligence Cases
              </div>
              <div className="mt-1 space-y-1">
                {filteredCases.map((c) => (
                  <button
                    key={c.title}
                    onClick={() => handleSelect(c.href)}
                    className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-slate-100 dark:hover:bg-white/[0.05] border border-transparent hover:border-slate-200 dark:hover:border-white/[0.06] transition-all group text-left"
                  >
                    <div className="flex items-center gap-2.5">
                      <ShieldAlert className="h-4 w-4 text-red-500 dark:text-red-400 shrink-0" />
                      <span className="text-xs font-medium text-slate-800 dark:text-white/80 group-hover:text-slate-900 dark:group-hover:text-white">
                        {c.title}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-slate-500 dark:text-white/40 flex items-center gap-1">
                        <MapPin className="h-3 w-3 text-slate-400 dark:text-white/30" /> {c.location}
                      </span>
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-red-500/10 text-red-500 dark:text-red-400 border border-red-500/20">
                        {c.status}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Footer Bar */}
          <div className="px-4 py-2.5 bg-slate-50 dark:bg-white/[0.02] border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between text-[11px] text-slate-500 dark:text-white/30">
            <div className="flex items-center gap-2">
              <Sparkles className="h-3.5 w-3.5 text-accent" />
              <span>Sentinel Security Copilot v4.2 Command Index</span>
            </div>
            <div className="flex items-center gap-3">
              <span>Use <kbd className="font-mono text-slate-600 dark:text-white/50">↑↓</kbd> to navigate</span>
              <span><kbd className="font-mono text-slate-600 dark:text-white/50">↵</kbd> to select</span>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
