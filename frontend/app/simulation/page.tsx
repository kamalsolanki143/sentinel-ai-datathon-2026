"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import {
  Activity,
  Play,
  Sliders,
  ShieldCheck,
  AlertTriangle,
  TrendingDown,
  MapPin,
  Cpu,
  RefreshCw,
  Sparkles,
  CloudRain,
  Users,
  Shield,
} from "lucide-react";
import MetricCard from "@/components/Cards/MetricCard";
import PageHeader from "@/components/Common/PageHeader";
import StatusBadge from "@/components/Common/StatusBadge";
import SimulationCharts, { HourlySimData, SectorImpactData } from "@/components/Simulation/SimulationCharts";
import { motion, AnimatePresence } from "framer-motion";

const HeatMap = dynamic(() => import("@/components/HeatMap/HeatMap"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-slate-100 dark:bg-[#050816] animate-pulse rounded-2xl flex items-center justify-center border border-slate-200 dark:border-white/[0.08]">
      <span className="text-slate-500 dark:text-white/40 text-xs font-mono flex items-center gap-2">
        <Activity className="h-4 w-4 animate-spin text-primary" />
        LOADING SPATIAL HEATMAP MODEL...
      </span>
    </div>
  ),
});

export default function SimulationPage() {
  const [scenario, setScenario] = useState("Operation Iron Curtain");
  const [location, setLocation] = useState("Sector 4 - Downtown");
  const [timeHorizon, setTimeHorizon] = useState("24 Hours");
  const [weather, setWeather] = useState("Heavy Rain");
  const [patrolAllocation, setPatrolAllocation] = useState(85);

  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  // Dynamic simulation metrics
  const [mitigationRate, setMitigationRate] = useState(42.5);
  const [threatScore, setThreatScore] = useState(88);
  const [patrolEfficiency, setPatrolEfficiency] = useState(94.2);
  const [projectedIncidents, setProjectedIncidents] = useState(14);

  const [hourlyChartData, setHourlyChartData] = useState<HourlySimData[]>([
    { time: "00:00", baseline: 35, simulated: 18 },
    { time: "04:00", baseline: 22, simulated: 10 },
    { time: "08:00", baseline: 45, simulated: 25 },
    { time: "12:00", baseline: 68, simulated: 32 },
    { time: "16:00", baseline: 92, simulated: 44 },
    { time: "20:00", baseline: 85, simulated: 38 },
    { time: "23:59", baseline: 50, simulated: 22 },
  ]);

  const [sectorChartData, setSectorChartData] = useState<SectorImpactData[]>([
    { sector: "Sec 1 Commercial", before: 78, after: 38 },
    { sector: "Sec 2 Harbor", before: 84, after: 42 },
    { sector: "Sec 3 Suburbs", before: 45, after: 20 },
    { sector: "Sec 4 Downtown", before: 96, after: 48 },
    { sector: "Sec 5 Industrial", before: 62, after: 28 },
  ]);

  const runSimulation = () => {
    setIsRunning(true);
    setProgress(0);

    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setIsRunning(false);
          // Randomize new outputs
          setMitigationRate(parseFloat((40 + Math.random() * 15).toFixed(1)));
          setThreatScore(Math.floor(70 + Math.random() * 20));
          setPatrolEfficiency(parseFloat((90 + Math.random() * 8).toFixed(1)));
          setProjectedIncidents(Math.floor(8 + Math.random() * 10));
          return 100;
        }
        return prev + 20;
      });
    }, 300);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Threat Simulation Engine"
        subtitle="Monte Carlo predictive spatio-temporal scenario modeling & getaway trajectory estimation."
        breadcrumbs={[
          { label: "Command Center", href: "/dashboard" },
          { label: "Crime Simulation" },
        ]}
        icon={Activity}
        statusBadge={<StatusBadge variant="success">SIMULATION CORE v4.2</StatusBadge>}
      />

      {/* Main Grid: Scenario Builder & Simulator Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Interactive Scenario Builder */}
        <div className="lg:col-span-4 rounded-3xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl p-5 shadow-md dark:shadow-xl space-y-5 transition-colors duration-300">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3.5">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-xl bg-accent/10 text-accent border border-accent/20">
                <Sliders className="h-4 w-4" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">Scenario Parameters</h3>
            </div>
            <span className="text-[10px] font-mono text-accent font-bold px-2 py-0.5 rounded bg-accent/10">
              PREDICTIVE
            </span>
          </div>

          <div className="space-y-4 text-xs font-sans">
            <div>
              <label className="text-[11px] font-semibold text-slate-500 dark:text-white/40 block mb-1">
                PRESET SCENARIO
              </label>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:border-primary font-mono text-xs"
              >
                <option value="Operation Iron Curtain">Operation Iron Curtain (Bank Robbery Escape)</option>
                <option value="Port Terminal Lockdown">Port Terminal Lockdown (Contraband Transfer)</option>
                <option value="Civil Unrest Perimeter">Civil Unrest Perimeter Defense</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-semibold text-slate-500 dark:text-white/40 block mb-1">
                TARGET JURISDICTION
              </label>
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:border-primary font-mono text-xs"
              >
                <option value="Sector 4 - Downtown">Sector 4 - Downtown Commercial</option>
                <option value="Sector 2 - Harbor Expressway">Sector 2 - Harbor Expressway</option>
                <option value="Sector 1 - Industrial Zone">Sector 1 - Industrial Zone</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[11px] font-semibold text-slate-500 dark:text-white/40 block mb-1">
                  WEATHER CONDITION
                </label>
                <select
                  value={weather}
                  onChange={(e) => setWeather(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:border-primary font-mono text-xs"
                >
                  <option value="Heavy Rain">Heavy Rain</option>
                  <option value="Dense Fog">Dense Fog</option>
                  <option value="Clear Sky">Clear Sky</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] font-semibold text-slate-500 dark:text-white/40 block mb-1">
                  HORIZON
                </label>
                <select
                  value={timeHorizon}
                  onChange={(e) => setTimeHorizon(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-50 dark:bg-white/[0.04] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white focus:outline-none focus:border-primary font-mono text-xs"
                >
                  <option value="12 Hours">12 Hours</option>
                  <option value="24 Hours">24 Hours</option>
                  <option value="48 Hours">48 Hours</option>
                </select>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-[11px] font-semibold text-slate-500 dark:text-white/40">
                  PATROL UNIT ALLOCATION ({patrolAllocation}%)
                </label>
              </div>
              <input
                type="range"
                min="10"
                max="100"
                value={patrolAllocation}
                onChange={(e) => setPatrolAllocation(Number(e.target.value))}
                className="w-full accent-primary"
              />
            </div>
          </div>

          {/* Action Trigger Button */}
          <button
            onClick={runSimulation}
            disabled={isRunning}
            className="w-full py-3.5 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-2xl shadow-xl shadow-primary/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
          >
            {isRunning ? (
              <>
                <Cpu className="h-4 w-4 animate-spin text-white" /> EXECUTING 10,000 MONTE CARLO RUNS ({progress}%)
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-current" /> RUN SIMULATION MODEL
              </>
            )}
          </button>
        </div>

        {/* Right Column: Simulation Output & Impact Analysis */}
        <div className="lg:col-span-8 space-y-6">
          {/* KPI Output Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              title="Risk Reduction Rate"
              value={`-${mitigationRate}%`}
              change="+5.2%"
              trend="down"
              icon={TrendingDown}
              status="success"
              sparklineData={[20, 25, 30, 38, 42.5]}
            />
            <MetricCard
              title="Threat Score"
              value={`${threatScore} / 100`}
              change="Elevated"
              trend="up"
              icon={AlertTriangle}
              status="danger"
              sparklineData={[70, 75, 82, 85, 88]}
            />
            <MetricCard
              title="Patrol Efficiency"
              value={`${patrolEfficiency}%`}
              change="+1.4%"
              trend="up"
              icon={ShieldCheck}
              status="success"
              sparklineData={[88, 90, 92, 93.5, 94.2]}
            />
            <MetricCard
              title="Projected Incidents"
              value={projectedIncidents}
              change="-4 cases"
              trend="down"
              icon={Cpu}
              status="neutral"
              sparklineData={[22, 19, 17, 15, 14]}
            />
          </div>

          {/* Simulation Output Charts */}
          <SimulationCharts hourlyData={hourlyChartData} sectorData={sectorChartData} />
        </div>
      </div>
    </div>
  );
}
