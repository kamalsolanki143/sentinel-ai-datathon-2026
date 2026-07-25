"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BrainCircuit,
  Network,
  Activity,
  FileText,
  BellRing,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const primaryNav = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard, category: "Core Operations" },
  { title: "AI Security Copilot", href: "/copilot", icon: BrainCircuit, category: "Core Operations", highlight: true },
  { title: "Network Intel", href: "/network-analysis", icon: Network, category: "Investigative Analytics" },
  { title: "Crime Simulation", href: "/simulation", icon: Activity, category: "Investigative Analytics" },
  { title: "Reports Library", href: "/reports", icon: FileText, category: "Documentation" },
  { title: "Threat Alerts", href: "/alerts", icon: BellRing, category: "Threat Response", badge: 3 },
];

const secondaryNav = [
  { title: "System Settings", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  // Hide sidebar on landing/login/auth pages
  if (pathname === "/" || pathname.startsWith("/login") || pathname.startsWith("/signup") || pathname.startsWith("/forgot") || pathname.startsWith("/verify") || pathname.startsWith("/reset")) {
    return null;
  }

  return (
    <>
      {/* Desktop Floating Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 72 : 260 }}
        transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] as const }}
        className="hidden md:flex flex-col fixed left-0 top-[56px] bottom-0 z-40 border-r border-slate-200/80 dark:border-white/[0.08] bg-white/95 dark:bg-[#050816]/95 backdrop-blur-2xl shadow-xl transition-colors duration-300"
      >
        {/* Navigation Section */}
        <nav className="flex-1 py-4 px-3 flex flex-col gap-1 overflow-y-auto no-scrollbar">
          {/* Header Tag */}
          <div className={`px-2 mb-2 flex items-center justify-between ${collapsed ? "justify-center" : ""}`}>
            <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400 dark:text-white/30">
              {collapsed ? "•••" : "COMMAND MODULES"}
            </span>
            {!collapsed && (
              <span className="h-1.5 w-1.5 rounded-full bg-primary animate-ping" />
            )}
          </div>

          {/* Navigation Items */}
          {primaryNav.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link key={item.href} href={item.href}>
                <div
                  className={`group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-semibold transition-all duration-200 ${
                    isActive
                      ? "bg-primary/10 dark:bg-gradient-to-r dark:from-primary/20 dark:to-accent/10 text-primary dark:text-white border border-primary/30 shadow-md dark:shadow-primary/10"
                      : "text-slate-600 dark:text-white/50 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.04] border border-transparent"
                  } ${collapsed ? "justify-center px-0" : ""}`}
                >
                  {/* Glowing active bar */}
                  {isActive && (
                    <motion.div
                      layoutId="sidebar-pill"
                      className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-r-full bg-gradient-to-b from-primary to-accent"
                      transition={{ type: "spring", stiffness: 350, damping: 30 }}
                    />
                  )}

                  <div className={`relative shrink-0 ${isActive ? "text-primary" : "text-slate-400 dark:text-white/40 group-hover:text-slate-700 dark:group-hover:text-white/80"}`}>
                    <item.icon className="h-4 w-4" strokeWidth={isActive ? 2.2 : 1.8} />
                    {item.highlight && !isActive && (
                      <span className="absolute -top-0.5 -right-0.5 h-1.5 w-1.5 rounded-full bg-accent animate-pulse" />
                    )}
                  </div>

                  <AnimatePresence>
                    {!collapsed && (
                      <motion.span
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: "auto" }}
                        exit={{ opacity: 0, width: 0 }}
                        className="whitespace-nowrap overflow-hidden flex-1"
                      >
                        {item.title}
                      </motion.span>
                    )}
                  </AnimatePresence>

                  {/* Badge */}
                  {item.badge && !collapsed && (
                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-full bg-red-500/10 text-red-500 dark:bg-red-500/20 dark:text-red-400 border border-red-500/30">
                      {item.badge}
                    </span>
                  )}
                </div>
              </Link>
            );
          })}

          <div className="my-3 border-t border-slate-200/80 dark:border-white/[0.06]" />

          {/* Secondary Nav */}
          {secondaryNav.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link key={item.href} href={item.href}>
                <div
                  className={`group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-xs font-medium transition-all ${
                    isActive
                      ? "bg-primary/10 text-primary border border-primary/20"
                      : "text-slate-500 dark:text-white/40 hover:text-slate-900 dark:hover:text-white/80 hover:bg-slate-100 dark:hover:bg-white/[0.04]"
                  } ${collapsed ? "justify-center px-0" : ""}`}
                >
                  <item.icon className="h-4 w-4 shrink-0" strokeWidth={1.8} />
                  {!collapsed && <span className="whitespace-nowrap">{item.title}</span>}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Footer Collapse Button & User Status */}
        <div className="p-3 border-t border-slate-200/80 dark:border-white/[0.08] bg-slate-50/50 dark:bg-white/[0.01]">
          {!collapsed && (
            <div className="p-2.5 rounded-xl bg-slate-100 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[10px] font-mono text-slate-500 dark:text-white/50">SECURE SESSION</span>
              </div>
              <span className="text-[9px] font-mono text-primary font-bold px-1 rounded bg-primary/10">L5</span>
            </div>
          )}

          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center gap-2 py-2 rounded-xl text-xs text-slate-500 dark:text-white/40 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.05] border border-slate-200 dark:border-white/[0.06] transition-all"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <><ChevronLeft className="h-4 w-4" /> Collapse Panel</>}
          </button>
        </div>
      </motion.aside>

      {/* Mobile Bottom Navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 dark:bg-[#050816]/95 backdrop-blur-xl border-t border-slate-200 dark:border-white/[0.08] px-3 py-2 flex items-center justify-around">
        {primaryNav.slice(0, 5).map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href} className="flex flex-col items-center gap-1">
              <div className={`p-1.5 rounded-xl transition-colors ${isActive ? "bg-primary text-white" : "text-slate-400 dark:text-white/40"}`}>
                <item.icon className="h-4 w-4" />
              </div>
              <span className={`text-[9px] font-medium ${isActive ? "text-primary" : "text-slate-400 dark:text-white/30"}`}>
                {item.title.split(" ")[0]}
              </span>
            </Link>
          );
        })}
      </div>
    </>
  );
}
