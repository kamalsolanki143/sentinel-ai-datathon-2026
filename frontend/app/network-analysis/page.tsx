"use client";

import React, { useState } from "react";
import {
  Network,
  Search,
  Users,
  ShieldAlert,
  PhoneCall,
  FileSpreadsheet,
  MapPin,
  Sparkles,
} from "lucide-react";
import MetricCard from "@/components/Cards/MetricCard";
import PageHeader from "@/components/Common/PageHeader";
import StatusBadge from "@/components/Common/StatusBadge";
import NetworkGraph, { NetworkNode, NetworkEdge } from "@/components/Network/NetworkGraph";
import EntityProfileModal from "@/components/Network/EntityProfileModal";
import Link from "next/link";

const mockNodes: NetworkNode[] = [
  {
    id: "node-1",
    name: "Marcus Vance",
    alias: "Viper",
    type: "kingpin",
    syndicate: "Viper Syndicate",
    riskScore: 96,
    role: "Syndicate Boss / Strategist",
    lastLocation: "Sector 4 - Downtown Hotel Suite #901",
    warrants: 4,
    x: 48,
    y: 35,
  },
  {
    id: "node-2",
    name: "Viktor Thorne",
    alias: "The Hammer",
    type: "kingpin",
    syndicate: "Apex Cartel",
    riskScore: 92,
    role: "Armed Operations Commander",
    lastLocation: "Sector 2 - Harbor Warehouse B",
    warrants: 6,
    x: 72,
    y: 25,
  },
  {
    id: "node-3",
    name: "Darius Black",
    alias: "Shadow",
    type: "associate",
    syndicate: "Viper Syndicate",
    riskScore: 84,
    role: "Logistics & Getaway Lead",
    lastLocation: "Sector 4 - Commercial District",
    warrants: 2,
    x: 32,
    y: 45,
  },
  {
    id: "node-4",
    name: "Elena Rostova",
    alias: "Broker",
    type: "associate",
    syndicate: "Viper Syndicate",
    riskScore: 78,
    role: "Crypto Money Launderer",
    lastLocation: "Sector 1 - Financial Tower",
    warrants: 1,
    x: 58,
    y: 60,
  },
  {
    id: "node-5",
    name: "Apex Logistics LLC",
    type: "front_company",
    syndicate: "Viper Syndicate",
    riskScore: 68,
    role: "Shell Import/Export Corporation",
    lastLocation: "Sector 2 - Port Gate 4",
    warrants: 0,
    x: 75,
    y: 58,
  },
  {
    id: "node-6",
    name: "Jax Miller",
    alias: "Ghost",
    type: "associate",
    syndicate: "Apex Cartel",
    riskScore: 81,
    role: "Weapons Procurement Specialist",
    lastLocation: "Sector 5 - Industrial Zone",
    warrants: 3,
    x: 85,
    y: 40,
  },
];

const mockEdges: NetworkEdge[] = [
  { id: "e-1-3", source: "node-1", target: "node-3", type: "command", label: "Direct Orders" },
  { id: "e-1-4", source: "node-1", target: "node-4", type: "financial", label: "Crypto Transfer", amount: "$1.4M" },
  { id: "e-4-5", source: "node-4", target: "node-5", type: "financial", label: "Shell Account" },
  { id: "e-2-6", source: "node-2", target: "node-6", type: "command", label: "Weapons Contract" },
  { id: "e-1-2", source: "node-1", target: "node-2", type: "co_offender", label: "Cartel Non-Aggression Pact" },
];

export default function NetworkAnalysisPage() {
  const [selectedNodeId, setSelectedNodeId] = useState<string>("node-1");
  const [searchQuery, setSearchQuery] = useState("");
  const [syndicateFilter, setSyndicateFilter] = useState("All");
  const [typeFilter, setTypeFilter] = useState("All");
  const [minRiskFilter, setMinRiskFilter] = useState(0);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const selectedNode = mockNodes.find((n) => n.id === selectedNodeId) || mockNodes[0];
  const connectedEdges = mockEdges.filter(
    (e) => e.source === selectedNode.id || e.target === selectedNode.id
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Criminal Network Intelligence"
        subtitle="Graph topology, syndicate hierarchy mapping, and wiretap communications analysis."
        icon={Network}
        statusBadge={<StatusBadge status="1,204 NODES MAPPED" variant="info" />}
      >
        <button
          onClick={() => alert("Exported Network Topology Graph PDF")}
          className="px-4 py-2 bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-800 dark:text-white border border-slate-200 dark:border-white/[0.08] text-xs font-semibold rounded-xl transition-all flex items-center gap-2 shadow-sm"
        >
          <FileSpreadsheet className="h-4 w-4 text-emerald-500 dark:text-emerald-400" /> Export Topology
        </button>
      </PageHeader>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Monitored Entities"
          value="1,204"
          icon={Users}
          trend="up"
          change="+18 this week"
          variant="primary"
        />
        <MetricCard
          title="Active Syndicates"
          value={4}
          icon={Network}
          trend="neutral"
          change="Viper, Apex, Shadow, Red"
          variant="accent"
        />
        <MetricCard
          title="High Risk Bosses"
          value={12}
          icon={ShieldAlert}
          trend="up"
          change="Warrants Active"
          variant="danger"
        />
        <MetricCard
          title="Wiretaps Intercepted"
          value="342"
          icon={PhoneCall}
          trend="up"
          change="+45 today"
          variant="warning"
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
              placeholder="Search by suspect name, alias, or role..."
              className="w-full h-9 pl-9 pr-3 rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08] text-xs text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-white/30 focus:outline-none focus:border-primary/50 transition-all"
            />
          </div>

          <select
            value={syndicateFilter}
            onChange={(e) => setSyndicateFilter(e.target.value)}
            className="h-9 px-3 rounded-xl bg-white dark:bg-[#050816] border border-slate-200 dark:border-white/[0.08] text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
          >
            <option value="All">All Syndicates</option>
            <option value="Viper Syndicate">Viper Syndicate</option>
            <option value="Apex Cartel">Apex Cartel</option>
          </select>

          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="h-9 px-3 rounded-xl bg-white dark:bg-[#050816] border border-slate-200 dark:border-white/[0.08] text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
          >
            <option value="All">All Entity Types</option>
            <option value="kingpin">Kingpin / Boss</option>
            <option value="associate">Operative / Associate</option>
            <option value="front_company">Front Company</option>
          </select>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono text-slate-500 dark:text-white/50">
          <span>MIN RISK:</span>
          <input
            type="range"
            min="0"
            max="90"
            step="10"
            value={minRiskFilter}
            onChange={(e) => setMinRiskFilter(Number(e.target.value))}
            className="w-24 accent-primary"
          />
          <span className="font-bold text-primary">{minRiskFilter}%+</span>
        </div>
      </div>

      {/* Main Canvas + Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[640px]">
        {/* Network Topology Graph (2 cols) */}
        <div className="lg:col-span-2 h-full">
          <NetworkGraph
            nodes={mockNodes}
            edges={mockEdges}
            selectedNodeId={selectedNodeId}
            onSelectNode={(id) => setSelectedNodeId(id)}
            searchQuery={searchQuery}
            syndicateFilter={syndicateFilter}
            typeFilter={typeFilter}
            minRiskFilter={minRiskFilter}
          />
        </div>

        {/* Selected Node Details Inspector Panel (1 col) */}
        <div className="h-full rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/80 backdrop-blur-xl p-5 flex flex-col justify-between overflow-y-auto space-y-4 shadow-sm dark:shadow-2xl no-scrollbar transition-colors duration-300">
          {/* Header Node Banner */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-2xl bg-red-500/10 dark:bg-gradient-to-br dark:from-red-500/20 dark:to-accent/20 border border-red-500/30 flex items-center justify-center text-red-500 dark:text-red-400 font-mono font-bold text-lg shadow-md">
                  {selectedNode.name.charAt(0)}
                </div>
                <div>
                  <h3 className="font-bold text-sm text-slate-900 dark:text-white">{selectedNode.name}</h3>
                  {selectedNode.alias && (
                    <span className="text-xs font-mono text-primary">Alias: "{selectedNode.alias}"</span>
                  )}
                </div>
              </div>
              <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-full bg-red-500/10 text-red-500 dark:text-red-400 border border-red-500/20">
                {selectedNode.riskScore}% RISK
              </span>
            </div>

            {/* Quick Details Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.06]">
                <span className="text-slate-400 dark:text-white/30 text-[10px] block font-mono">AFFILIATION</span>
                <span className="text-slate-900 dark:text-white font-bold">{selectedNode.syndicate}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/[0.06]">
                <span className="text-slate-400 dark:text-white/30 text-[10px] block font-mono">WARRANTS</span>
                <span className="text-amber-500 dark:text-amber-400 font-bold font-mono">{selectedNode.warrants} Active</span>
              </div>
            </div>

            {/* Role & Location */}
            <div className="space-y-2 text-xs">
              <div>
                <span className="text-slate-400 dark:text-white/40 block text-[10px] uppercase font-mono">Role Description</span>
                <span className="text-slate-800 dark:text-white/90 font-medium">{selectedNode.role}</span>
              </div>
              <div>
                <span className="text-slate-400 dark:text-white/40 block text-[10px] uppercase font-mono">Last Known Location</span>
                <span className="text-slate-700 dark:text-white/80 flex items-center gap-1 mt-0.5">
                  <MapPin className="h-3.5 w-3.5 text-primary" /> {selectedNode.lastLocation}
                </span>
              </div>
            </div>

            {/* Connected Links */}
            <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-white/[0.08]">
              <h4 className="text-[10px] font-bold text-slate-400 dark:text-white/30 uppercase tracking-widest font-mono">
                Active Node Connections ({connectedEdges.length})
              </h4>
              <div className="space-y-1.5 text-xs">
                {connectedEdges.map((edge) => {
                  const otherNodeId = edge.source === selectedNode.id ? edge.target : edge.source;
                  const otherNode = mockNodes.find((n) => n.id === otherNodeId);
                  return (
                    <div
                      key={edge.id}
                      onClick={() => otherNode && setSelectedNodeId(otherNode.id)}
                      className="p-2 rounded-xl bg-slate-50 dark:bg-white/[0.03] hover:bg-slate-100 dark:hover:bg-white/[0.06] border border-slate-200 dark:border-white/[0.06] flex items-center justify-between cursor-pointer transition-colors"
                    >
                      <span className="text-slate-800 dark:text-white/80 font-medium">{otherNode?.name}</span>
                      <span className="text-[10px] font-mono text-primary px-1.5 py-0.5 rounded bg-primary/10">
                        {edge.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Action Trigger */}
          <div className="flex flex-col gap-2 mt-4">
            <button
              onClick={() => setShowProfileModal(true)}
              className="w-full py-2.5 bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-900 dark:text-white border border-slate-200 dark:border-white/10 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-2"
            >
              <Users className="h-4 w-4 text-primary" /> Full Entity Dossier Inspector
            </button>
            <Link
              href="/copilot"
              className="w-full py-2.5 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white text-xs font-bold rounded-xl shadow-lg shadow-primary/20 flex items-center justify-center gap-2 transition-all"
            >
              <Sparkles className="h-4 w-4" /> Query Node with Security Copilot
            </Link>
          </div>
        </div>
      </div>

      {/* Entity Profile Drawer Modal */}
      <EntityProfileModal
        node={showProfileModal ? selectedNode : null}
        onClose={() => setShowProfileModal(false)}
      />
    </div>
  );
}
