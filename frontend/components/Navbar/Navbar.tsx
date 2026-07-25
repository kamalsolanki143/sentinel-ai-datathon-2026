"use client";

import React, { useState, useEffect } from "react";
import {
  Bell,
  ShieldAlert,
  Search,
  ChevronDown,
  Menu,
  X,
  ExternalLink,
  Shield,
  SlidersHorizontal,
  Sun,
  Moon,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import CommandPalette from "@/components/Common/CommandPalette";
import { useTheme } from "@/components/Theme/ThemeProvider";

const breadcrumbMap: Record<string, string> = {
  "/dashboard": "Command Center",
  "/copilot": "AI Security Copilot",
  "/network-analysis": "Criminal Network Intel",
  "/simulation": "Threat Simulation Engine",
  "/reports": "Intelligence Reports",
  "/alerts": "Real-Time Threats",
  "/settings": "System & API Config",
};

interface NotificationItem {
  id: string;
  title: string;
  time: string;
  type: "critical" | "warning" | "info";
  unread: boolean;
}

export default function Navbar() {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const [notifications, setNotifications] = useState<NotificationItem[]>([
    { id: "1", title: "Commercial Bank Vault Alarm Triggered", time: "2m ago", type: "critical", unread: true },
    { id: "2", title: "Marcus Vance Node Location Updated", time: "14m ago", type: "warning", unread: true },
    { id: "3", title: "Copilot Report #REP-9041 Generated", time: "1h ago", type: "info", unread: false },
  ]);

  const hasUnread = notifications.some((n) => n.unread);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setShowCommandPalette((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  if (pathname === "/" || pathname.startsWith("/login") || pathname.startsWith("/signup") || pathname.startsWith("/forgot") || pathname.startsWith("/verify") || pathname.startsWith("/reset")) {
    return null;
  }

  const currentPage = Object.entries(breadcrumbMap).find(
    ([path]) => pathname === path || pathname.startsWith(path + "/")
  );

  return (
    <>
      <nav className="h-[56px] border-b border-slate-200/80 dark:border-white/[0.08] bg-white/80 dark:bg-[#050816]/90 backdrop-blur-xl z-50 flex items-center justify-between px-4 md:px-6 sticky top-0 shadow-sm dark:shadow-lg dark:shadow-black/40 transition-colors duration-300">
        {/* Left Section: Logo & Breadcrumbs */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            className="md:hidden p-1.5 rounded-lg text-slate-500 dark:text-white/50 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.05] transition-colors"
          >
            {showMobileMenu ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>

          <Link href="/dashboard" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary via-blue-500 to-accent flex items-center justify-center shadow-lg shadow-primary/25 group-hover:scale-105 transition-transform">
                <ShieldAlert className="h-5 w-5 text-white" strokeWidth={2.2} />
              </div>
              <div className="absolute -inset-0.5 rounded-xl bg-primary/40 opacity-0 group-hover:opacity-100 blur transition-opacity" />
            </div>

            <div className="hidden sm:flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="text-sm font-bold tracking-tight text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                  SENTINEL
                </span>
                <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 bg-primary/10 text-primary border border-primary/20 rounded">
                  v4.2
                </span>
              </div>
              <span className="text-[9px] font-mono text-slate-500 dark:text-white/40 uppercase tracking-[0.18em]">
                Crime Intel OS
              </span>
            </div>
          </Link>

          {/* Breadcrumb Separator */}
          {currentPage && (
            <div className="hidden md:flex items-center gap-2 text-xs">
              <span className="text-slate-300 dark:text-white/20">/</span>
              <span className="font-semibold text-slate-700 dark:text-white/80 tracking-wide flex items-center gap-1.5">
                {currentPage[1]}
              </span>
            </div>
          )}
        </div>

        {/* Center: Command Palette Trigger */}
        <div className="hidden lg:flex flex-1 justify-center max-w-lg mx-6">
          <button
            onClick={() => setShowCommandPalette(true)}
            className="w-full flex items-center justify-between h-9 px-3.5 rounded-xl bg-slate-100/80 dark:bg-white/[0.03] hover:bg-slate-200/80 dark:hover:bg-white/[0.06] border border-slate-200 dark:border-white/[0.08] hover:border-primary/40 text-xs text-slate-500 dark:text-white/40 hover:text-slate-900 dark:hover:text-white/80 transition-all shadow-inner group"
          >
            <div className="flex items-center gap-2.5">
              <Search className="h-3.5 w-3.5 text-primary group-hover:scale-110 transition-transform" />
              <span>Search intel, suspects, commands...</span>
            </div>
            <div className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-200 dark:bg-white/[0.06] text-slate-600 dark:text-white/40 border border-slate-300 dark:border-white/[0.08]">
                ⌘K
              </kbd>
            </div>
          </button>
        </div>

        {/* Right Section: Live Status, Theme Switcher, Notifications & Profile */}
        <div className="flex items-center gap-3">
          {/* Live System Status Pill */}
          <div className="hidden xl:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="font-mono text-[10px] tracking-wider uppercase">ONLINE • 99.8% ACCURACY</span>
          </div>

          {/* Theme Switcher Button */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/70 hover:text-slate-900 dark:hover:text-white border border-slate-200/80 dark:border-white/[0.08] transition-all shadow-sm"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          >
            <motion.div
              key={theme}
              initial={{ rotate: -90, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 90, opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              {theme === "dark" ? (
                <Sun className="h-4 w-4 text-amber-400" />
              ) : (
                <Moon className="h-4 w-4 text-slate-700" />
              )}
            </motion.div>
          </button>

          {/* Quick Command Trigger Button */}
          <button
            onClick={() => setShowCommandPalette(true)}
            className="lg:hidden p-2 rounded-xl bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-white/[0.08] transition-colors"
          >
            <Search className="h-4 w-4" />
          </button>

          {/* Notifications Button & Dropdown */}
          <div className="relative">
            <button
              onClick={() => {
                setShowNotifications(!showNotifications);
                setShowProfileMenu(false);
              }}
              className="relative p-2 rounded-xl bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-white/[0.08] transition-colors"
            >
              <Bell className="h-4 w-4" />
              {hasUnread && (
                <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-[#050816] animate-pulse" />
              )}
            </button>

            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.95 }}
                  className="absolute right-0 mt-2 w-80 rounded-2xl bg-white dark:bg-[#0f172a]/95 border border-slate-200 dark:border-white/[0.12] shadow-2xl backdrop-blur-xl z-50 overflow-hidden"
                >
                  <div className="p-3 border-b border-slate-100 dark:border-white/[0.08] flex items-center justify-between bg-slate-50 dark:bg-white/[0.02]">
                    <div className="flex items-center gap-2">
                      <ShieldAlert className="h-4 w-4 text-primary" />
                      <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">Threat Feeds</h3>
                    </div>
                    <button
                      onClick={() => setNotifications((prev) => prev.map((n) => ({ ...n, unread: false })))}
                      className="text-[10px] text-primary hover:underline font-mono"
                    >
                      Mark All as Read
                    </button>
                  </div>

                  <div className="p-2 space-y-1 max-h-72 overflow-y-auto no-scrollbar">
                    {notifications.map((n) => (
                      <div
                        key={n.id}
                        className={`p-2.5 rounded-xl transition-all border ${
                          n.unread
                            ? "bg-primary/5 dark:bg-primary/10 border-primary/20"
                            : "hover:bg-slate-100 dark:hover:bg-white/[0.05] border-transparent hover:border-slate-200 dark:hover:border-white/[0.06]"
                        } cursor-pointer`}
                      >
                        <div className="flex items-start justify-between">
                          <h4 className="text-xs font-semibold text-slate-800 dark:text-white/90 leading-snug flex items-center gap-1.5">
                            {n.unread && <span className="h-1.5 w-1.5 rounded-full bg-primary flex-shrink-0" />}
                            {n.title}
                          </h4>
                          <span className="text-[9px] text-slate-400 dark:text-white/30 font-mono whitespace-nowrap ml-2">{n.time}</span>
                        </div>
                        <div className="mt-1 flex items-center justify-between text-[10px]">
                          <span className={n.type === "critical" ? "text-red-500 font-bold" : "text-amber-500"}>
                            {n.type.toUpperCase()}
                          </span>
                          <Link
                            href="/alerts"
                            onClick={() => setShowNotifications(false)}
                            className="text-primary hover:underline flex items-center gap-0.5"
                          >
                            Inspect Threat <ExternalLink className="h-2.5 w-2.5" />
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>

                  <Link
                    href="/alerts"
                    onClick={() => setShowNotifications(false)}
                    className="block p-2.5 text-center text-xs font-semibold text-primary bg-primary/5 hover:bg-primary/10 border-t border-slate-100 dark:border-white/[0.08] transition-colors"
                  >
                    Open Live Threat Center →
                  </Link>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* User Profile Badge */}
          <div className="relative">
            <button
              onClick={() => {
                setShowProfileMenu(!showProfileMenu);
                setShowNotifications(false);
              }}
              className="flex items-center gap-2 p-1.5 rounded-xl bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] border border-slate-200 dark:border-white/[0.08] transition-colors"
            >
              <div className="h-6 w-6 rounded-lg bg-gradient-to-tr from-primary to-purple-600 flex items-center justify-center text-[10px] font-bold text-white shadow">
                KS
              </div>
              <span className="hidden md:inline text-xs font-semibold text-slate-800 dark:text-white/80">Capt. Solanki</span>
              <ChevronDown className="h-3.5 w-3.5 text-slate-400 dark:text-white/40" />
            </button>

            <AnimatePresence>
              {showProfileMenu && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.95 }}
                  className="absolute right-0 mt-2 w-56 rounded-2xl bg-white dark:bg-[#0f172a]/95 border border-slate-200 dark:border-white/[0.12] shadow-2xl backdrop-blur-xl z-50 p-2 space-y-1 text-xs"
                >
                  <div className="p-2 border-b border-slate-100 dark:border-white/[0.08] mb-1">
                    <p className="font-bold text-slate-900 dark:text-white">Capt. Kamal Solanki</p>
                    <p className="text-[10px] text-slate-400 dark:text-white/40 font-mono">Badge: BADGE-88402</p>
                    <span className="inline-block mt-1 text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold">
                      CLEARANCE LEVEL 5
                    </span>
                  </div>

                  <Link
                    href="/settings"
                    onClick={() => setShowProfileMenu(false)}
                    className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-white/[0.05] text-slate-700 dark:text-white/70 hover:text-slate-900 dark:hover:text-white transition-colors"
                  >
                    <SlidersHorizontal className="h-3.5 w-3.5 text-primary" />
                    System Settings
                  </Link>
                  <Link
                    href="/login"
                    onClick={() => setShowProfileMenu(false)}
                    className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-red-500/10 text-red-500 transition-colors"
                  >
                    <Shield className="h-3.5 w-3.5" />
                    Lock Command Session
                  </Link>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </nav>

      {/* Command Palette Component Modal */}
      <CommandPalette isOpen={showCommandPalette} onClose={() => setShowCommandPalette(false)} />
    </>
  );
}
