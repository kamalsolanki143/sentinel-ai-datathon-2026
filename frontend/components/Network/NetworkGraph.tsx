"use client";

import React, { useState } from "react";
import { ZoomIn, ZoomOut, Maximize2, Radio } from "lucide-react";
import { motion } from "framer-motion";
import { useTheme } from "@/components/Theme/ThemeProvider";

export interface NetworkNode {
  id: string;
  name: string;
  alias?: string;
  type: "kingpin" | "associate" | "front_company" | "vehicle" | "location";
  syndicate: string;
  riskScore: number;
  role: string;
  lastLocation: string;
  warrants: number;
  x: number; // percentage pos in SVG canvas (0 to 100)
  y: number; // percentage pos in SVG canvas (0 to 100)
  avatarBg?: string;
}

export interface NetworkEdge {
  id: string;
  source: string;
  target: string;
  type: "financial" | "co_offender" | "command" | "wiretap" | "kinship";
  label: string;
  amount?: string;
}

interface NetworkGraphProps {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
  searchQuery: string;
  syndicateFilter: string;
  typeFilter: string;
  minRiskFilter: number;
}

export default function NetworkGraph({
  nodes,
  edges,
  selectedNodeId,
  onSelectNode,
  searchQuery,
  syndicateFilter,
  typeFilter,
  minRiskFilter,
}: NetworkGraphProps) {
  const [zoomLevel, setZoomLevel] = useState(1);

  const isNodeVisible = (node: NetworkNode) => {
    if (minRiskFilter > 0 && node.riskScore < minRiskFilter) return false;
    if (syndicateFilter !== "All" && node.syndicate !== syndicateFilter) return false;
    if (typeFilter !== "All" && node.type !== typeFilter) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchName = node.name.toLowerCase().includes(q);
      const matchAlias = node.alias?.toLowerCase().includes(q);
      const matchRole = node.role.toLowerCase().includes(q);
      if (!matchName && !matchAlias && !matchRole) return false;
    }
    return true;
  };

  const getEdgeStyle = (type: NetworkEdge["type"]) => {
    switch (type) {
      case "command":
        return { stroke: "#ef4444", strokeWidth: 2.5, strokeDasharray: "none" };
      case "co_offender":
        return { stroke: "#f97316", strokeWidth: 2, strokeDasharray: "4 4" };
      case "financial":
        return { stroke: "#3b82f6", strokeWidth: 2, strokeDasharray: "none" };
      case "wiretap":
        return { stroke: "#8b5cf6", strokeWidth: 1.8, strokeDasharray: "2 3" };
      case "kinship":
        return { stroke: "#10b981", strokeWidth: 1.5, strokeDasharray: "6 3" };
      default:
        return { stroke: "#64748b", strokeWidth: 1.5, strokeDasharray: "none" };
    }
  };

  const getNodeColor = (node: NetworkNode) => {
    if (node.riskScore >= 90) return "#ef4444";
    if (node.riskScore >= 75) return "#f97316";
    if (node.riskScore >= 50) return "#f59e0b";
    return "#3b82f6";
  };

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 0.2, 1.8));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 0.2, 0.7));
  const handleResetZoom = () => setZoomLevel(1);

  return (
    <div className="relative w-full h-full min-h-[500px] rounded-2xl bg-white dark:bg-[#050816] border border-slate-200/80 dark:border-white/[0.08] overflow-hidden shadow-sm dark:shadow-2xl flex flex-col justify-between group transition-colors duration-300">
      {/* Background Cyber Grid */}
      <div className="absolute inset-0 cyber-grid opacity-30 pointer-events-none" />

      {/* Floating Canvas Controls */}
      <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 p-1.5 rounded-xl bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-xl border border-slate-200 dark:border-white/[0.1] shadow-xl">
        <button
          onClick={handleZoomIn}
          className="p-1.5 rounded-lg text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.08] transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="h-4 w-4" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-1.5 rounded-lg text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.08] transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="h-4 w-4" />
        </button>
        <button
          onClick={handleResetZoom}
          className="p-1.5 rounded-lg text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.08] transition-colors"
          title="Reset Zoom"
        >
          <Maximize2 className="h-4 w-4" />
        </button>
      </div>

      {/* Top Left Live Graph Badge */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-xl border border-slate-200 dark:border-white/[0.1] text-xs shadow-md">
        <Radio className="h-3.5 w-3.5 text-primary animate-pulse" />
        <span className="font-bold text-slate-900 dark:text-white uppercase tracking-wider text-[11px]">Syndicate Topology Canvas</span>
        <span className="font-mono text-[10px] text-slate-500 dark:text-white/40 border-l border-slate-200 dark:border-white/10 pl-2">
          {nodes.filter(isNodeVisible).length} ACTIVE NODES
        </span>
      </div>

      {/* SVG Canvas Area */}
      <div
        className="w-full h-full flex-1 relative overflow-hidden transition-transform duration-300"
        style={{ transform: `scale(${zoomLevel})` }}
      >
        <svg className="w-full h-full absolute inset-0 pointer-events-none">
          {/* Edge Lines */}
          {edges.map((edge) => {
            const sourceNode = nodes.find((n) => n.id === edge.source);
            const targetNode = nodes.find((n) => n.id === edge.target);

            if (!sourceNode || !targetNode) return null;
            if (!isNodeVisible(sourceNode) || !isNodeVisible(targetNode)) return null;

            const isSelected = selectedNodeId === sourceNode.id || selectedNodeId === targetNode.id;
            const style = getEdgeStyle(edge.type);

            return (
              <g key={edge.id}>
                <line
                  x1={`${sourceNode.x}%`}
                  y1={`${sourceNode.y}%`}
                  x2={`${targetNode.x}%`}
                  y2={`${targetNode.y}%`}
                  stroke={isSelected ? "#3b82f6" : style.stroke}
                  strokeWidth={isSelected ? style.strokeWidth + 1.5 : style.strokeWidth}
                  strokeDasharray={style.strokeDasharray}
                  opacity={isSelected ? 1 : 0.45}
                />
              </g>
            );
          })}
        </svg>

        {/* Nodes */}
        {nodes.map((node) => {
          if (!isNodeVisible(node)) return null;

          const isSelected = selectedNodeId === node.id;
          const nodeColor = getNodeColor(node);

          return (
            <motion.div
              key={node.id}
              onClick={() => onSelectNode(node.id)}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              whileHover={{ scale: 1.15 }}
              className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer z-10 group"
              style={{ left: `${node.x}%`, top: `${node.y}%` }}
            >
              {/* Radial Glowing Halo for Kingpins / High Risk */}
              {(node.type === "kingpin" || node.riskScore >= 90) && (
                <div
                  className="absolute inset-0 rounded-full blur-md opacity-60 animate-pulse"
                  style={{ background: nodeColor, padding: "12px" }}
                />
              )}

              {/* Node Vessel */}
              <div
                className={`relative flex items-center justify-center rounded-2xl p-2.5 transition-all shadow-xl backdrop-blur-xl border ${
                  isSelected
                    ? "ring-4 ring-primary/40 bg-white dark:bg-[#0f172a] border-primary scale-110 shadow-primary/30"
                    : "bg-white/90 dark:bg-[#0f172a]/90 border-slate-200 dark:border-white/[0.12] hover:border-slate-300 dark:hover:border-white/30"
                }`}
                style={{ borderColor: isSelected ? nodeColor : undefined }}
              >
                <div
                  className="h-8 w-8 rounded-xl flex items-center justify-center font-bold text-xs shadow-md font-mono"
                  style={{ backgroundColor: `${nodeColor}20`, color: nodeColor, border: `1px solid ${nodeColor}50` }}
                >
                  {node.name.charAt(0)}
                </div>

                <div className="ml-2.5 text-left hidden sm:block">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-primary transition-colors">
                      {node.name}
                    </span>
                    {node.alias && (
                      <span className="text-[9px] font-mono text-slate-400 dark:text-white/40">"{node.alias}"</span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[9px] font-mono font-bold px-1 rounded bg-slate-100 dark:bg-white/[0.06] text-slate-600 dark:text-white/60 uppercase">
                      {node.type}
                    </span>
                    <span className="text-[9px] font-mono font-bold" style={{ color: nodeColor }}>
                      RISK {node.riskScore}%
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Bottom Canvas Legend */}
      <div className="p-3 border-t border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/80 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4 text-xs z-20">
        <div className="flex items-center gap-4 text-[11px]">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-red-500" />
            <span className="text-slate-600 dark:text-white/60">Kingpin / Critical</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-amber-500" />
            <span className="text-slate-600 dark:text-white/60">Operative</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-blue-500" />
            <span className="text-slate-600 dark:text-white/60">Front / Asset</span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-[10px] text-slate-500 dark:text-white/40 font-mono">
          <span>COMMAND LINK: RED SOLID</span>
          <span>FINANCIAL LINK: BLUE SOLID</span>
        </div>
      </div>
    </div>
  );
}
