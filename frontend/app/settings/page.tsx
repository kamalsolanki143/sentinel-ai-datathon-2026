"use client";

import React, { useState } from "react";
import {
  Settings,
  User,
  Bell,
  Key,
  Globe,
  Cpu,
  ShieldCheck,
  Save,
  CheckCircle2,
  Lock,
  Activity,
  Check,
  Radio,
  Volume2,
  Mail,
  Smartphone,
  ShieldAlert,
  Send,
  Database,
  Server,
  Layers,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import PageHeader from "@/components/Common/PageHeader";
import SectionCard from "@/components/Common/SectionCard";
import StatusBadge from "@/components/Common/StatusBadge";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<
    "api" | "ai" | "map" | "profile" | "notifications" | "roles"
  >("api");

  // Form State
  const [officerName, setOfficerName] = useState("Capt. Kamal Solanki");
  const [officerBadge, setOfficerBadge] = useState("BADGE-88402");
  const [officerRank, setOfficerRank] = useState("Captain / Lead Architect");
  const [officerDept, setOfficerDept] = useState("AI Intelligence & Cyber Crimes");
  const [officerAgency, setOfficerAgency] = useState("Metro Law Enforcement Agency");
  const [officerEmail, setOfficerEmail] = useState("kamal@sentinel-ai.gov");
  const [officerContact, setOfficerContact] = useState("+1 (555) 904-2841");
  const [backendUrl, setBackendUrl] = useState("http://localhost:8000/api");
  const [apiKey, setApiKey] = useState("snt_live_99042a884f092e1189c");
  const [aiModel, setAiModel] = useState("Sentinel-GPT-v4.2-Neural");
  const [aiTemperature, setAiTemperature] = useState(0.2);
  const [mapTileStyle, setMapTileStyle] = useState("CartoDB Dark Matter");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Notification Toggles
  const [notifs, setNotifs] = useState({
    emailAlerts: true,
    pushNotifs: true,
    emergencyBroadcast: true,
    smsAlerts: false,
    threatNotifs: true,
    investigationUpdates: true,
    dailyReports: true,
    soundAlerts: true,
  });

  // Role Permissions Matrix State
  const [permissions, setPermissions] = useState<Record<string, Record<string, boolean>>>({
    Administrator: {
      viewDashboard: true,
      manageOfficers: true,
      manageReports: true,
      exportReports: true,
      broadcastAlerts: true,
      accessCopilot: true,
      manageAiModels: true,
      editSettings: true,
    },
    Supervisor: {
      viewDashboard: true,
      manageOfficers: false,
      manageReports: true,
      exportReports: true,
      broadcastAlerts: true,
      accessCopilot: true,
      manageAiModels: false,
      editSettings: false,
    },
    Officer: {
      viewDashboard: true,
      manageOfficers: false,
      manageReports: true,
      exportReports: true,
      broadcastAlerts: false,
      accessCopilot: true,
      manageAiModels: false,
      editSettings: false,
    },
    Analyst: {
      viewDashboard: true,
      manageOfficers: false,
      manageReports: true,
      exportReports: true,
      broadcastAlerts: false,
      accessCopilot: true,
      manageAiModels: false,
      editSettings: false,
    },
  });

  const toggleNotif = (key: keyof typeof notifs) => {
    setNotifs((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const togglePermission = (role: string, permKey: string) => {
    setPermissions((prev) => ({
      ...prev,
      [role]: {
        ...prev[role],
        [permKey]: !prev[role][permKey],
      },
    }));
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setToastMessage("System configurations successfully saved & synchronized to Sentinel Core!");
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleTestNotification = () => {
    setToastMessage("TEST BROADCAST: Dispatching test emergency alert to officer terminal...");
    setTimeout(() => setToastMessage(null), 3500);
  };

  return (
    <div className="space-y-6">
      {/* Toast Notification */}
      <AnimatePresence>
        {toastMessage && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-20 right-6 z-50 p-3.5 bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 rounded-2xl shadow-2xl font-mono text-xs font-bold flex items-center gap-2 backdrop-blur-xl"
          >
            <CheckCircle2 className="h-4 w-4 text-emerald-500 dark:text-emerald-400" />
            {toastMessage}
          </motion.div>
        )}
      </AnimatePresence>

      <PageHeader
        title="System Settings & Infrastructure Control"
        subtitle="Configure backend REST endpoints, Security Copilot model parameters, spatial maps, and security permissions."
        icon={Settings}
        statusBadge={<StatusBadge status="SETTINGS SYNCHRONIZED" variant="success" />}
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Navigation Tabs & System Health (Left 1 col) */}
        <div className="lg:col-span-1 space-y-6">
          <div className="rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/80 backdrop-blur-xl p-3 space-y-1.5 shadow-sm dark:shadow-xl transition-colors duration-300">
            {[
              { id: "api", label: "Backend URL & API Keys", icon: Key },
              { id: "ai", label: "AI Copilot Parameters", icon: Cpu },
              { id: "map", label: "Spatial Map Settings", icon: Globe },
              { id: "profile", label: "Officer Profile", icon: User },
              { id: "notifications", label: "Notification Triggers", icon: Bell },
              { id: "roles", label: "Role & Permissions", icon: ShieldCheck },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() =>
                    setActiveTab(
                      tab.id as "profile" | "api" | "ai" | "map" | "notifications" | "roles"
                    )
                  }
                  className={`w-full text-left p-3 rounded-xl text-xs font-semibold flex items-center gap-3 transition-all ${
                    isActive
                      ? "bg-gradient-to-r from-primary to-accent text-white shadow-lg shadow-primary/20"
                      : "text-slate-500 dark:text-white/40 hover:bg-slate-100 dark:hover:bg-white/[0.04] hover:text-slate-900 dark:hover:text-white/90"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* System Health Widget */}
          <div className="rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/80 backdrop-blur-xl p-4 space-y-3 font-mono text-xs shadow-sm dark:shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-2">
              <span className="font-bold text-slate-900 dark:text-white uppercase tracking-wider text-[10px] flex items-center gap-1.5">
                <Activity className="h-3.5 w-3.5 text-emerald-500" /> SYSTEM HEALTH
              </span>
              <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 font-bold border border-emerald-500/20">
                100% HEALTHY
              </span>
            </div>

            <div className="space-y-2 text-[11px]">
              {[
                { name: "Backend REST API", status: "Online", latency: "12ms" },
                { name: "Database Cluster", status: "Healthy", latency: "4ms" },
                { name: "AI Inference Engine", status: "Online", latency: "84ms" },
                { name: "Spatial Tile Maps", status: "Online", latency: "18ms" },
                { name: "Notification Hub", status: "Online", latency: "6ms" },
              ].map((sub, i) => (
                <div key={i} className="flex items-center justify-between text-slate-600 dark:text-white/60">
                  <span className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    {sub.name}
                  </span>
                  <span className="text-slate-400 dark:text-white/40">{sub.latency}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Tab Content (Right 3 cols) */}
        <div className="lg:col-span-3 space-y-6">
          <form onSubmit={handleSave}>
            {activeTab === "api" && (
              <SectionCard
                title="Backend API & Infrastructure Endpoint"
                subtitle="Configure REST API host and secure access tokens"
                icon={Key}
              >
                <div className="space-y-4 text-xs">
                  <div>
                    <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                      Sentinel Backend API URL
                    </label>
                    <input
                      type="url"
                      value={backendUrl}
                      onChange={(e) => setBackendUrl(e.target.value)}
                      required
                      className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] px-3 font-mono text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                    />
                  </div>

                  <div>
                    <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                      Encrypted API Secret Token
                    </label>
                    <input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      required
                      className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] px-3 font-mono text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                    />
                  </div>
                </div>
              </SectionCard>
            )}

            {activeTab === "ai" && (
              <SectionCard
                title="Security Copilot Model Parameters"
                subtitle="Configure LLM model version and inference temperature"
                icon={Cpu}
              >
                <div className="space-y-4 text-xs">
                  <div>
                    <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                      AI Neural Model Version
                    </label>
                    <select
                      value={aiModel}
                      onChange={(e) => setAiModel(e.target.value)}
                      className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-[#050816] px-3 text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
                    >
                      <option value="Sentinel-GPT-v4.2-Neural">Sentinel-GPT-v4.2-Neural (Default)</option>
                      <option value="Copilot-Tactical-Llama3-70B">Copilot-Tactical-Llama3-70B</option>
                      <option value="Graph-Inference-Engine-v2">Graph-Inference-Engine-v2</option>
                    </select>
                  </div>

                  <div>
                    <div className="flex justify-between items-center mb-1">
                      <label className="font-semibold text-slate-700 dark:text-white/70 uppercase tracking-wider text-[10px]">
                        Inference Temperature
                      </label>
                      <span className="font-mono text-primary font-bold">{aiTemperature}</span>
                    </div>
                    <input
                      type="range"
                      min="0.0"
                      max="1.0"
                      step="0.05"
                      value={aiTemperature}
                      onChange={(e) => setAiTemperature(Number(e.target.value))}
                      className="w-full accent-primary"
                    />
                  </div>
                </div>
              </SectionCard>
            )}

            {activeTab === "map" && (
              <SectionCard
                title="Spatial Map Provider & Layer Settings"
                subtitle="Configure dark map tiles and update frequencies"
                icon={Globe}
              >
                <div className="space-y-4 text-xs">
                  <div>
                    <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                      Map Tile Style
                    </label>
                    <select
                      value={mapTileStyle}
                      onChange={(e) => setMapTileStyle(e.target.value)}
                      className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-[#050816] px-3 text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
                    >
                      <option value="CartoDB Dark Matter">CartoDB Dark Matter (Recommended)</option>
                      <option value="Mapbox Dark Vector">Mapbox Dark Vector</option>
                      <option value="OpenStreetMap Dark">OpenStreetMap Dark</option>
                    </select>
                  </div>
                </div>
              </SectionCard>
            )}

            {activeTab === "profile" && (
              <SectionCard
                title="Command Officer Profile"
                subtitle="Personal badge identifier, rank clearance, and officer metadata"
                icon={User}
              >
                <div className="space-y-6 text-xs">
                  {/* Officer Header Card */}
                  <div className="p-4 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] flex flex-col sm:flex-row items-center gap-4">
                    <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center font-bold text-white text-xl shadow-lg font-mono">
                      KS
                    </div>
                    <div className="space-y-1 text-center sm:text-left flex-1">
                      <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
                        <h3 className="font-bold text-base text-slate-900 dark:text-white">{officerName}</h3>
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-mono text-[10px] font-bold border border-emerald-500/20">
                          CLEARANCE LEVEL 5
                        </span>
                      </div>
                      <p className="text-xs text-primary font-semibold">{officerRank}</p>
                      <p className="text-[11px] text-slate-500 dark:text-white/40">{officerAgency} • {officerDept}</p>
                    </div>
                    <div className="font-mono text-right text-[10px] text-slate-400 dark:text-white/40 hidden md:block">
                      <p>LAST LOGIN: Today 09:42 EST</p>
                      <p className="text-emerald-500 font-bold">SESSION: ACTIVE</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                        Officer Full Name
                      </label>
                      <input
                        type="text"
                        value={officerName}
                        onChange={(e) => setOfficerName(e.target.value)}
                        className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] px-3 text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
                      />
                    </div>
                    <div>
                      <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                        Badge Identifier
                      </label>
                      <input
                        type="text"
                        value={officerBadge}
                        onChange={(e) => setOfficerBadge(e.target.value)}
                        className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] px-3 font-mono text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
                      />
                    </div>
                    <div>
                      <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                        Official Agency Email
                      </label>
                      <input
                        type="email"
                        value={officerEmail}
                        onChange={(e) => setOfficerEmail(e.target.value)}
                        className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] px-3 text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
                      />
                    </div>
                    <div>
                      <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                        Direct Contact Phone
                      </label>
                      <input
                        type="text"
                        value={officerContact}
                        onChange={(e) => setOfficerContact(e.target.value)}
                        className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] px-3 font-mono text-xs text-slate-900 dark:text-white focus:outline-none transition-all"
                      />
                    </div>
                  </div>
                </div>
              </SectionCard>
            )}

            {activeTab === "notifications" && (
              <SectionCard
                title="Notification Triggers & Dispatch Alerts"
                subtitle="Configure multi-channel alerts and real-time emergency broadcasts"
                icon={Bell}
              >
                <div className="space-y-6 text-xs">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {[
                      { key: "emailAlerts", label: "Email Alerts", desc: "Dispatch urgent intelligence digests to official email", icon: Mail },
                      { key: "pushNotifs", label: "Push Notifications", desc: "Real-time desktop browser notifications", icon: Bell },
                      { key: "emergencyBroadcast", label: "Emergency Broadcast", desc: "Override terminal audio for DEFCON 1 alerts", icon: Radio },
                      { key: "smsAlerts", label: "SMS Alerts", desc: "SMS messages to verified officer phone", icon: Smartphone },
                      { key: "threatNotifs", label: "Threat Notifications", desc: "Alerts when GNN flags critical risk nodes", icon: ShieldAlert },
                      { key: "investigationUpdates", label: "Investigation Updates", desc: "Copilot case workspace activity feeds", icon: Layers },
                      { key: "dailyReports", label: "Daily Intelligence Digest", desc: "Automated 08:00 EST daily crime report", icon: Database },
                      { key: "soundAlerts", label: "Sound Alerts", desc: "Tactical chime for incoming ANPR camera hits", icon: Volume2 },
                    ].map((item) => {
                      const Icon = item.icon;
                      const isEnabled = notifs[item.key as keyof typeof notifs];
                      return (
                        <div
                          key={item.key}
                          onClick={() => toggleNotif(item.key as keyof typeof notifs)}
                          className="p-3.5 rounded-2xl border border-slate-200/80 dark:border-white/[0.06] bg-slate-50 dark:bg-white/[0.02] flex items-start justify-between cursor-pointer hover:border-primary/40 transition-colors"
                        >
                          <div className="space-y-1 pr-2">
                            <div className="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
                              <Icon className="h-4 w-4 text-primary" />
                              <span>{item.label}</span>
                            </div>
                            <p className="text-[11px] text-slate-500 dark:text-white/50 leading-relaxed">
                              {item.desc}
                            </p>
                          </div>
                          <div
                            className={`w-11 h-6 rounded-full p-1 transition-colors flex items-center ${
                              isEnabled ? "bg-primary justify-end" : "bg-slate-300 dark:bg-white/20 justify-start"
                            }`}
                          >
                            <span className="h-4 w-4 rounded-full bg-white shadow-sm" />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div className="pt-2 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between">
                    <span className="text-xs text-slate-500 dark:text-white/40">Verify dispatcher connection state</span>
                    <button
                      type="button"
                      onClick={handleTestNotification}
                      className="px-4 py-2 bg-slate-100 dark:bg-white/[0.05] hover:bg-slate-200 dark:hover:bg-white/10 text-slate-800 dark:text-white rounded-xl border border-slate-200 dark:border-white/10 text-xs font-semibold flex items-center gap-2 transition-all"
                    >
                      <Send className="h-3.5 w-3.5 text-primary" /> Send Test Notification
                    </button>
                  </div>
                </div>
              </SectionCard>
            )}

            {activeTab === "roles" && (
              <SectionCard
                title="Role & Permissions Matrix"
                subtitle="Granular security access rules across agency operational roles"
                icon={ShieldCheck}
              >
                <div className="space-y-6 text-xs">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left font-mono">
                      <thead>
                        <tr className="border-b border-slate-200 dark:border-white/[0.08] text-[10px] text-slate-400 dark:text-white/40 uppercase">
                          <th className="py-2.5 px-3">Permission Scope</th>
                          <th className="py-2.5 px-3 text-center">Administrator</th>
                          <th className="py-2.5 px-3 text-center">Supervisor</th>
                          <th className="py-2.5 px-3 text-center">Officer</th>
                          <th className="py-2.5 px-3 text-center">Analyst</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04]">
                        {[
                          { key: "viewDashboard", label: "View Command Dashboard" },
                          { key: "manageOfficers", label: "Manage Officer Accounts" },
                          { key: "manageReports", label: "Create & Edit Reports" },
                          { key: "exportReports", label: "Export Signed Dossiers" },
                          { key: "broadcastAlerts", label: "Broadcast Threat Alerts" },
                          { key: "accessCopilot", label: "Access Security Copilot" },
                          { key: "manageAiModels", label: "Configure Neural Models" },
                          { key: "editSettings", label: "Modify System Settings" },
                        ].map((perm) => (
                          <tr key={perm.key} className="hover:bg-slate-50 dark:hover:bg-white/[0.02]">
                            <td className="py-3 px-3 font-sans font-medium text-slate-800 dark:text-white/80 text-xs">
                              {perm.label}
                            </td>
                            {["Administrator", "Supervisor", "Officer", "Analyst"].map((role) => {
                              const checked = permissions[role]?.[perm.key] ?? false;
                              return (
                                <td key={role} className="py-3 px-3 text-center">
                                  <input
                                    type="checkbox"
                                    checked={checked}
                                    onChange={() => togglePermission(role, perm.key)}
                                    className="rounded border-slate-300 dark:border-white/20 bg-slate-100 dark:bg-white/5 text-primary h-4 w-4 cursor-pointer"
                                  />
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </SectionCard>
            )}

            {/* Save Button */}
            <div className="mt-6 flex justify-end">
              <button
                type="submit"
                className="px-6 py-2.5 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary/20 flex items-center gap-2 transition-all"
              >
                <Save className="h-4 w-4" /> Save System Configurations
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
