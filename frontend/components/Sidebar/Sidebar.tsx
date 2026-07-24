"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, BrainCircuit, Network, Activity, FileText } from "lucide-react";

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "Intelligence Copilot",
    href: "/copilot",
    icon: BrainCircuit,
  },
  {
    title: "Network Analysis",
    href: "/network-analysis",
    icon: Network,
  },
  {
    title: "Crime Simulation",
    href: "/simulation",
    icon: Activity,
  },
  {
    title: "Reports",
    href: "/reports",
    icon: FileText,
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-card flex-shrink-0 hidden md:flex flex-col">
      <div className="flex-1 py-6 px-3 flex flex-col gap-2">
        <div className="px-3 mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Command Modules
        </div>
        {navItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200 ${
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
            >
              <item.icon className={`h-5 w-5 ${isActive ? "text-primary" : ""}`} />
              {item.title}
            </Link>
          );
        })}
      </div>
      <div className="p-4 border-t border-border">
        <div className="bg-destructive/10 border border-destructive/20 rounded-md p-3">
          <div className="flex items-center gap-2 text-destructive font-medium text-sm mb-1">
            <div className="h-2 w-2 rounded-full bg-destructive animate-pulse" />
            System Status
          </div>
          <p className="text-xs text-muted-foreground">DEFCON 3 - Active Monitoring</p>
        </div>
      </div>
    </aside>
  );
}
