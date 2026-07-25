"use client";

import React, { useState } from "react";
import {
  FileText,
  Search,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  ArrowUpDown,
  ExternalLink,
  MapPin,
} from "lucide-react";
import Link from "next/link";

interface Incident {
  id: string;
  type: string;
  location: string;
  timestamp: string;
  priority: "Critical" | "High" | "Medium" | "Low";
  status: "Active" | "Investigating" | "Resolved";
  assignedUnit: string;
}

const mockIncidents: Incident[] = [
  { id: "INC-8901", type: "Commercial Bank Vault Alarm", location: "Sector 4 - Downtown", timestamp: "23:42 EST", priority: "Critical", status: "Active", assignedUnit: "Unit Alpha-4" },
  { id: "INC-8902", type: "Armored Vehicle Theft", location: "Sector 2 - Port Expressway", timestamp: "22:15 EST", priority: "High", status: "Investigating", assignedUnit: "Unit Bravo-2" },
  { id: "INC-8903", type: "Cyber Wiretap Signal Intercept", location: "Sector 4 - Financial Dist.", timestamp: "20:05 EST", priority: "Critical", status: "Active", assignedUnit: "Cyber Unit-9" },
  { id: "INC-8904", type: "Warehouse Fire & Explosion", location: "Sector 1 - North Docks", timestamp: "18:40 EST", priority: "Medium", status: "Resolved", assignedUnit: "Unit Charlie-1" },
  { id: "INC-8905", type: "ANPR Stolen SUV Sighting", location: "Sector 3 - Suburb Toll", timestamp: "17:10 EST", priority: "High", status: "Investigating", assignedUnit: "Unit Patrol-7" },
];

export default function IncidentsTable() {
  const [search, setSearch] = useState("");
  const [priorityFilter, setPriorityFilter] = useState<string>("All");
  const [currentPage, setCurrentPage] = useState(1);

  const filteredIncidents = mockIncidents.filter((inc) => {
    const matchesSearch = inc.type.toLowerCase().includes(search.toLowerCase()) ||
                          inc.id.toLowerCase().includes(search.toLowerCase()) ||
                          inc.location.toLowerCase().includes(search.toLowerCase());
    const matchesPriority = priorityFilter === "All" || inc.priority === priorityFilter;
    return matchesSearch && matchesPriority;
  });

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-md dark:shadow-xl space-y-4 transition-colors duration-300">
      {/* Table Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 dark:border-white/[0.08] pb-3.5">
        <div>
          <h3 className="font-bold text-sm text-slate-900 dark:text-white flex items-center gap-2">
            Active Incident Intelligence Log
            <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-primary/10 text-primary border border-primary/20">
              REAL-TIME DATABASE
            </span>
          </h3>
          <p className="text-[11px] text-slate-500 dark:text-white/40 mt-0.5">
            Verified CAD calls and spatial dispatch telemetry
          </p>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search incident ID, type..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:border-primary w-44 font-sans"
            />
          </div>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-white/80 focus:outline-none focus:border-primary font-mono"
          >
            <option value="All">All Priority</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
          </select>
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-sans">
          <thead className="bg-slate-50/80 dark:bg-white/[0.02] border-b border-slate-200/80 dark:border-white/[0.08] text-[10px] font-mono text-slate-500 dark:text-white/40 uppercase">
            <tr>
              <th className="p-3 font-semibold">Incident ID</th>
              <th className="p-3 font-semibold">Classification</th>
              <th className="p-3 font-semibold">Location</th>
              <th className="p-3 font-semibold">Priority</th>
              <th className="p-3 font-semibold">Status</th>
              <th className="p-3 font-semibold">Assigned Unit</th>
              <th className="p-3 text-right font-semibold">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04]">
            {filteredIncidents.map((inc) => (
              <tr key={inc.id} className="hover:bg-slate-50/60 dark:hover:bg-white/[0.02] transition-colors">
                <td className="p-3 font-mono font-bold text-slate-900 dark:text-white">{inc.id}</td>
                <td className="p-3 font-semibold text-slate-800 dark:text-white/90">{inc.type}</td>
                <td className="p-3 text-slate-500 dark:text-white/60">
                  <span className="flex items-center gap-1 font-mono text-[11px]">
                    <MapPin className="h-3 w-3 text-primary" /> {inc.location}
                  </span>
                </td>
                <td className="p-3 font-mono">
                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${
                    inc.priority === "Critical"
                      ? "bg-red-500/10 text-red-500 border border-red-500/20"
                      : inc.priority === "High"
                      ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                      : "bg-blue-500/10 text-blue-500 border border-blue-500/20"
                  }`}>
                    {inc.priority}
                  </span>
                </td>
                <td className="p-3 font-mono">
                  <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${
                    inc.status === "Active"
                      ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                      : inc.status === "Investigating"
                      ? "bg-purple-500/10 text-purple-500 border border-purple-500/20"
                      : "bg-slate-500/10 text-slate-400 border border-slate-500/20"
                  }`}>
                    {inc.status}
                  </span>
                </td>
                <td className="p-3 font-mono text-slate-600 dark:text-white/70 text-[11px]">{inc.assignedUnit}</td>
                <td className="p-3 text-right">
                  <Link
                    href="/reports"
                    className="text-xs font-semibold text-primary hover:underline inline-flex items-center gap-1"
                  >
                    Dossier <ExternalLink className="h-3 w-3" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="pt-3 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between text-xs text-slate-500 dark:text-white/40 font-mono">
        <span>Showing 1 to {filteredIncidents.length} of {mockIncidents.length} entries</span>
        <div className="flex items-center gap-2">
          <button className="p-1 rounded-lg border border-slate-200 dark:border-white/10 opacity-50 cursor-not-allowed">
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="px-2 py-0.5 rounded bg-primary/10 text-primary font-bold">1</span>
          <button className="p-1 rounded-lg border border-slate-200 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/10">
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
