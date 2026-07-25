"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  BrainCircuit,
  Network,
  Activity,
  FileText,
  ArrowRight,
  ShieldCheck,
  Zap,
  Sparkles,
  Lock,
  Globe,
  Sun,
  Moon,
  Menu,
  X,
  ChevronDown,
  CheckCircle2,
  Mail,
  Database,
  Cpu,
  Radio,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { FaGithub, FaLinkedin } from "react-icons/fa";
import { useTheme } from "@/components/Theme/ThemeProvider";

export default function LandingPage() {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activePreviewTab, setActivePreviewTab] = useState<"command" | "copilot" | "network" | "reports">("command");
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const toggleFaq = (idx: number) => {
    setOpenFaq(openFaq === idx ? null : idx);
  };

  const faqList = [
    {
      q: "How does Sentinel AI maintain CJIS Level 5 compliance and security?",
      a: "Sentinel AI enforces end-to-end 256-bit AES encryption at rest and in transit, multi-factor CAC/PIV biometric authentication, and granular role-based access control (RBAC). All intelligence dossier queries produce immutable cryptographic hash signatures on an audit log chain.",
    },
    {
      q: "What AI models power the Security Copilot and Crime Prediction Engine?",
      a: "Our reasoning pipeline combines fine-tuned LLMs with custom graph neural networks (GNNs) and Monte Carlo spatio-temporal simulations to project incident density curves up to 48 hours in advance with 99.8% model precision.",
    },
    {
      q: "Can Sentinel AI integrate with existing agency Record Management Systems (RMS)?",
      a: "Yes. Sentinel AI features standardized REST APIs and GraphQL endpoints designed for seamless ingestion of legacy CAD, ANPR camera networks, wiretap logs, and RMS database schemas.",
    },
    {
      q: "Does the system support both Dark and Light theme preferences?",
      a: "Yes. Sentinel AI features a complete enterprise theme system with dynamic contrast adjustment, theme persistence, system preference auto-detection, and spatial dark/light map tile rendering.",
    },
  ];

  return (
    <div className="min-h-screen w-full bg-slate-50 dark:bg-[#050816] text-slate-900 dark:text-white relative overflow-hidden transition-colors duration-300 font-sans">
      {/* Background Ambient Particles & Mesh */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="orb absolute -top-40 -left-40 w-[650px] h-[650px] bg-primary/20" />
        <div className="orb absolute top-1/3 -right-40 w-[550px] h-[550px] bg-accent/20" style={{ animationDelay: "-7s" }} />
        <div className="orb absolute -bottom-40 left-1/3 w-[450px] h-[450px] bg-primary/15" style={{ animationDelay: "-14s" }} />
        <div className="cyber-grid absolute inset-0 opacity-15 dark:opacity-25" />
      </div>

      {/* 1. Sticky Navigation Bar */}
      <header className="fixed top-0 left-0 right-0 z-50 h-16 border-b border-slate-200/80 dark:border-white/[0.08] bg-white/85 dark:bg-[#050816]/85 backdrop-blur-xl px-4 md:px-8 lg:px-12 flex items-center justify-between shadow-sm transition-colors duration-300">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary via-blue-500 to-accent flex items-center justify-center shadow-lg shadow-primary/30 group-hover:scale-105 transition-transform">
            <ShieldAlert className="h-5 w-5 text-white" strokeWidth={2.2} />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-bold tracking-tight text-slate-900 dark:text-white">SENTINEL AI</span>
              <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 bg-primary/10 text-primary border border-primary/20 rounded">
                v4.2 PROD
              </span>
            </div>
            <span className="text-[9px] font-mono text-slate-500 dark:text-white/40 uppercase tracking-[0.18em] block">
              Crime Intel OS
            </span>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="hidden lg:flex items-center gap-6 text-xs font-semibold text-slate-600 dark:text-white/70">
          <a href="#features" className="hover:text-primary transition-colors">Features</a>
          <a href="#workflow" className="hover:text-primary transition-colors">AI Workflow</a>
          <a href="#preview" className="hover:text-primary transition-colors">Platform Preview</a>
          <a href="#comparison" className="hover:text-primary transition-colors">Why Sentinel</a>
          <a href="#team" className="hover:text-primary transition-colors">Team</a>
          <a href="#faq" className="hover:text-primary transition-colors">FAQ</a>
        </nav>

        {/* Actions & Theme Toggle */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/70 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-white/[0.08] transition-colors shadow-sm"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} Mode`}
          >
            {theme === "dark" ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-slate-700" />}
          </button>

          <Link
            href="/login"
            className="hidden sm:inline-block text-xs font-semibold text-slate-600 dark:text-white/70 hover:text-slate-900 dark:hover:text-white transition-colors px-3 py-1.5"
          >
            Officer Sign In
          </Link>

          <Link
            href="/dashboard"
            className="px-4 py-2 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary/25 flex items-center gap-2 transition-all"
          >
            Command Center <ArrowRight className="h-3.5 w-3.5" />
          </Link>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl text-slate-600 dark:text-white/60 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.05]"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </header>

      {/* Mobile Drawer Navigation */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="lg:hidden fixed top-16 left-0 right-0 z-40 bg-white/95 dark:bg-[#050816]/95 backdrop-blur-2xl border-b border-slate-200 dark:border-white/[0.08] p-4 space-y-3 text-xs font-semibold shadow-2xl"
          >
            <a href="#features" onClick={() => setMobileMenuOpen(false)} className="block p-2 text-slate-700 dark:text-white/80">Features</a>
            <a href="#workflow" onClick={() => setMobileMenuOpen(false)} className="block p-2 text-slate-700 dark:text-white/80">AI Workflow</a>
            <a href="#preview" onClick={() => setMobileMenuOpen(false)} className="block p-2 text-slate-700 dark:text-white/80">Platform Preview</a>
            <a href="#team" onClick={() => setMobileMenuOpen(false)} className="block p-2 text-slate-700 dark:text-white/80">Team</a>
            <a href="#faq" onClick={() => setMobileMenuOpen(false)} className="block p-2 text-slate-700 dark:text-white/80">FAQ</a>
            <div className="pt-2 border-t border-slate-100 dark:border-white/[0.08] flex items-center justify-between">
              <Link href="/login" onClick={() => setMobileMenuOpen(false)} className="text-primary font-bold">Officer Sign In</Link>
              <Link href="/signup" onClick={() => setMobileMenuOpen(false)} className="text-accent font-bold">Register Account</Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 2. Hero Section */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28 pb-16 text-center space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-4 max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-xs font-mono text-primary font-bold shadow-inner">
            <Sparkles className="h-3.5 w-3.5 text-accent animate-pulse" />
            AI-POWERED CRIME INTELLIGENCE & DECISION OPERATING SYSTEM
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.1]">
            Predictive AI Operations for <br className="hidden sm:inline" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-500 to-accent">
              Modern Law Enforcement
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-600 dark:text-white/60 max-w-2xl mx-auto leading-relaxed">
            Unifying spatial heatmaps, Security Copilot reasoning, criminal syndicate graph topology, and 48h Monte Carlo threat simulation into one enterprise platform.
          </p>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            href="/dashboard"
            className="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-primary via-blue-600 to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-sm rounded-2xl shadow-xl shadow-primary/30 flex items-center justify-center gap-2.5 transition-all"
          >
            Launch Command Center <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/copilot"
            className="w-full sm:w-auto px-8 py-3.5 bg-white/90 dark:bg-white/[0.04] hover:bg-slate-100 dark:hover:bg-white/[0.08] text-slate-800 dark:text-white border border-slate-200 dark:border-white/[0.1] font-bold text-sm rounded-2xl transition-all flex items-center justify-center gap-2 shadow-sm"
          >
            <BrainCircuit className="h-4 w-4 text-accent" /> Try Security Copilot
          </Link>
        </motion.div>

        {/* Hero Interactive Visualizer Mockup */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.25 }}
          className="pt-6 relative max-w-5xl mx-auto"
        >
          <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.12] bg-white/90 dark:bg-[#0f172a]/80 backdrop-blur-2xl p-4 sm:p-6 shadow-2xl dark:shadow-[#000000]/80 relative overflow-hidden group">
            {/* Visualizer Header */}
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3 mb-4 text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-red-500 inline-block" />
                <span className="h-3 w-3 rounded-full bg-amber-500 inline-block" />
                <span className="h-3 w-3 rounded-full bg-emerald-500 inline-block" />
                <span className="ml-2 font-bold text-slate-900 dark:text-white">SENTINEL RADAR V4.2</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold">
                <Radio className="h-3.5 w-3.5 animate-pulse" /> LIVE TELEMETRY STREAM
              </div>
            </div>

            {/* Mock Dashboard Graphics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              <div className="p-4 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] space-y-2">
                <span className="text-[10px] font-mono text-slate-400 dark:text-white/40 block">INCIDENT VELOCITY</span>
                <div className="text-xl font-bold font-mono text-slate-900 dark:text-white">142 Active</div>
                <div className="w-full bg-slate-200 dark:bg-white/10 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-red-500 h-full w-[78%]" />
                </div>
                <span className="text-[9px] font-mono text-red-500 font-bold block">+12.4% vs 24h Baseline</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] space-y-2">
                <span className="text-[10px] font-mono text-slate-400 dark:text-white/40 block">COPILOT NEURAL INFERENCE</span>
                <div className="text-xl font-bold font-mono text-slate-900 dark:text-white">Marcus Vance</div>
                <span className="inline-block text-[9px] font-mono px-2 py-0.5 rounded bg-accent/20 text-accent font-bold">
                  96% SYNDICATE MATCH
                </span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] space-y-2">
                <span className="text-[10px] font-mono text-slate-400 dark:text-white/40 block">MONTE CARLO PROJECTION</span>
                <div className="text-xl font-bold font-mono text-emerald-600 dark:text-emerald-400">-42.5% Risk</div>
                <span className="text-[9px] font-mono text-slate-500 dark:text-white/50 block">Sector 4 Optimized Patrols</span>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* 3. Trusted By & Technology Badges Section */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-10 border-y border-slate-200/80 dark:border-white/[0.08] bg-slate-100/50 dark:bg-white/[0.01]">
        <div className="text-center space-y-4">
          <p className="text-[10px] font-mono font-bold uppercase tracking-[0.25em] text-slate-400 dark:text-white/40">
            ENTERPRISE COMPLIANCE & TECHNOLOGY STACK
          </p>

          <div className="flex flex-wrap items-center justify-center gap-6 text-xs font-mono text-slate-600 dark:text-white/60 font-semibold">
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08]">
              <ShieldCheck className="h-4 w-4 text-emerald-500" /> FBI CJIS LEVEL 5
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08]">
              <Lock className="h-4 w-4 text-primary" /> NIST SP 800-53
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08]">
              <Globe className="h-4 w-4 text-accent" /> AWS GOVCLOUD
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08]">
              <Zap className="h-4 w-4 text-amber-500" /> NEXT.JS 16 & REACT 19
            </span>
          </div>
        </div>
      </section>

      {/* 4. Features Section */}
      <section id="features" className="relative z-10 max-w-6xl mx-auto px-6 py-20 space-y-12">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <span className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-primary px-3 py-1 rounded-full bg-primary/10 border border-primary/20">
            SYSTEM CAPABILITIES
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
            Built for High-Stakes Law Enforcement Operations
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-white/50">
            Every feature designed to provide maximum situational awareness and decision speed.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              title: "AI Security Copilot",
              desc: "Query complex case files, wiretaps, and ANPR databases in plain English with instant Cypher graph inference.",
              icon: BrainCircuit,
              href: "/copilot",
              color: "text-accent",
            },
            {
              title: "Spatial Heatmap Matrix",
              desc: "CartoDB powered spatial radar displaying incident intensity clusters, active patrols, and risk zones.",
              icon: Globe,
              href: "/dashboard",
              color: "text-primary",
            },
            {
              title: "Syndicate Network Intel",
              desc: "Graph topology canvas uncovering kingpin relationships, shell front companies, and money laundering ties.",
              icon: Network,
              href: "/network-analysis",
              color: "text-amber-500",
            },
            {
              title: "Monte Carlo Simulator",
              desc: "Simulate tactical patrol reallocations and project 24h risk reduction curves before unit dispatch.",
              icon: Activity,
              href: "/simulation",
              color: "text-emerald-600 dark:text-emerald-400",
            },
            {
              title: "Automated AI Dossiers",
              desc: "Generate official intelligence reports with Top Secret classification headers and cryptographic signatures.",
              icon: FileText,
              href: "/reports",
              color: "text-purple-500",
            },
            {
              title: "DEFCON Emergency Feeds",
              desc: "Real-time alert streaming with automated dispatch triggers and emergency broadcast overrides.",
              icon: ShieldAlert,
              href: "/alerts",
              color: "text-red-500",
            },
          ].map((card, idx) => (
            <Link key={idx} href={card.href}>
              <div className="p-6 rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 hover:bg-slate-50 dark:hover:bg-white/[0.04] hover:border-slate-300 dark:hover:border-white/20 transition-all space-y-4 group h-full shadow-sm dark:shadow-xl">
                <div className={`p-3 rounded-xl bg-slate-100 dark:bg-white/[0.05] border border-slate-200 dark:border-white/10 w-fit ${card.color} group-hover:scale-110 transition-transform`}>
                  <card.icon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-slate-900 dark:text-white group-hover:text-primary transition-colors">{card.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-white/50 mt-1 leading-relaxed">{card.desc}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 5. AI Workflow Section */}
      <section id="workflow" className="relative z-10 max-w-6xl mx-auto px-6 py-16 space-y-12">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <span className="text-[10px] font-mono font-bold uppercase tracking-[0.2em] text-accent px-3 py-1 rounded-full bg-accent/10 border border-accent/20">
            INTELLIGENCE PIPELINE
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
            From Raw Telemetry to Tactical Dispatch
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { step: "01", title: "Ingest Data", desc: "CAD feeds, CCTV ANPR scans, wiretap logs, and RMS records.", icon: Database },
            { step: "02", title: "Analyze Topology", desc: "Construct GNN entity graphs linking suspects, assets, & locations.", icon: Network },
            { step: "03", title: "Predict Escapes", desc: "Execute 10,000 Monte Carlo runs to model getaway vectors.", icon: Cpu },
            { step: "04", title: "Recommend Action", desc: "Security Copilot dispatches optimized patrol units.", icon: CheckCircle2 },
          ].map((item, idx) => (
            <div key={idx} className="p-5 rounded-2xl bg-white/80 dark:bg-[#0f172a]/60 border border-slate-200/80 dark:border-white/[0.08] space-y-3 text-left shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xl font-extrabold font-mono text-primary">{item.step}</span>
                <item.icon className="h-5 w-5 text-slate-400 dark:text-white/30" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">{item.title}</h3>
              <p className="text-xs text-slate-500 dark:text-white/40 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 6. Live Dashboard Preview Section */}
      <section id="preview" className="relative z-10 max-w-6xl mx-auto px-6 py-16 space-y-8">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
            Interactive Operational Preview
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-white/50">
            Switch between core intelligence modules below
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex flex-wrap justify-center gap-2 p-1.5 rounded-2xl bg-white/80 dark:bg-[#0f172a]/80 border border-slate-200 dark:border-white/[0.08] max-w-xl mx-auto text-xs font-semibold shadow-sm">
          {[
            { id: "command", label: "Command Center" },
            { id: "copilot", label: "Security Copilot" },
            { id: "network", label: "Network Intel" },
            { id: "reports", label: "Intelligence Reports" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActivePreviewTab(tab.id as "command" | "copilot" | "network" | "reports")}
              className={`px-4 py-2 rounded-xl transition-all ${
                activePreviewTab === tab.id
                  ? "bg-primary text-white shadow font-bold"
                  : "text-slate-600 dark:text-white/50 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Preview Container */}
        <div className="rounded-3xl border border-slate-200/80 dark:border-white/[0.12] bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-2xl p-6 shadow-2xl min-h-[320px] flex items-center justify-center">
          {activePreviewTab === "command" && (
            <div className="w-full space-y-4 text-left">
              <div className="flex justify-between items-center border-b border-slate-100 dark:border-white/[0.08] pb-3">
                <span className="font-bold text-sm text-slate-900 dark:text-white">Command Center Overview</span>
                <span className="text-xs font-mono text-emerald-500 font-bold">142 ACTIVE INCIDENTS</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-white/70">
                Spatial threat radar, real-time telemetry feeds, and active patrol unit coverage.
              </p>
              <Link href="/dashboard" className="inline-flex items-center gap-2 text-xs font-bold text-primary hover:underline">
                Explore Full Command Center →
              </Link>
            </div>
          )}

          {activePreviewTab === "copilot" && (
            <div className="w-full space-y-4 text-left">
              <div className="flex justify-between items-center border-b border-slate-100 dark:border-white/[0.08] pb-3">
                <span className="font-bold text-sm text-slate-900 dark:text-white">Security Copilot Query</span>
                <span className="text-xs font-mono text-accent font-bold">NEURAL INFERENCE ACTIVE</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-white/70">
                Natural language query stream analyzing suspect Marcus Vance and generating Cypher graph queries.
              </p>
              <Link href="/copilot" className="inline-flex items-center gap-2 text-xs font-bold text-accent hover:underline">
                Open Security Copilot →
              </Link>
            </div>
          )}

          {activePreviewTab === "network" && (
            <div className="w-full space-y-4 text-left">
              <div className="flex justify-between items-center border-b border-slate-100 dark:border-white/[0.08] pb-3">
                <span className="font-bold text-sm text-slate-900 dark:text-white">Criminal Network Graph</span>
                <span className="text-xs font-mono text-amber-500 font-bold">1,204 NODES MAPPED</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-white/70">
                Syndicate hierarchy canvas mapping boss nodes, shell front companies, and money laundering links.
              </p>
              <Link href="/network-analysis" className="inline-flex items-center gap-2 text-xs font-bold text-amber-500 hover:underline">
                Inspect Network Graph →
              </Link>
            </div>
          )}

          {activePreviewTab === "reports" && (
            <div className="w-full space-y-4 text-left">
              <div className="flex justify-between items-center border-b border-slate-100 dark:border-white/[0.08] pb-3">
                <span className="font-bold text-sm text-slate-900 dark:text-white">Intelligence Reports Library</span>
                <span className="text-xs font-mono text-purple-500 font-bold">TOP SECRET // LEVEL 5</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-white/70">
                Automated report synthesis producing encrypted dossier PDFs with cryptographic signatures.
              </p>
              <Link href="/reports" className="inline-flex items-center gap-2 text-xs font-bold text-purple-500 hover:underline">
                View Intelligence Library →
              </Link>
            </div>
          )}
        </div>
      </section>

      {/* 7. Statistics Counters */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-[#0f172a] to-slate-900 border border-white/[0.1] text-center text-white shadow-2xl">
          <div>
            <div className="text-3xl sm:text-4xl font-extrabold font-mono text-primary">1,204</div>
            <span className="text-xs text-white/50 mt-1 block">Monitored Entities</span>
          </div>
          <div>
            <div className="text-3xl sm:text-4xl font-extrabold font-mono text-emerald-400">99.8%</div>
            <span className="text-xs text-white/50 mt-1 block">Model Precision</span>
          </div>
          <div>
            <div className="text-3xl sm:text-4xl font-extrabold font-mono text-accent">&lt; 1.2s</div>
            <span className="text-xs text-white/50 mt-1 block">Inference Latency</span>
          </div>
          <div>
            <div className="text-3xl sm:text-4xl font-extrabold font-mono text-amber-400">-42.5%</div>
            <span className="text-xs text-white/50 mt-1 block">Risk Reduction</span>
          </div>
        </div>
      </section>

      {/* 8. Traditional vs Sentinel AI Comparison */}
      <section id="comparison" className="relative z-10 max-w-6xl mx-auto px-6 py-16 space-y-8">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
            Traditional RMS vs Sentinel AI OS
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-white/50">
            Why modern intelligence requires predictive graph neural networks
          </p>
        </div>

        <div className="overflow-x-auto rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 shadow-sm">
          <table className="w-full text-left text-xs font-sans">
            <thead>
              <tr className="border-b border-slate-200 dark:border-white/[0.08] text-slate-400 dark:text-white/40 font-mono uppercase text-[10px]">
                <th className="py-3 px-4">Capability / Feature</th>
                <th className="py-3 px-4 text-red-500">Traditional Police RMS</th>
                <th className="py-3 px-4 text-primary">Sentinel AI Operating System</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04]">
              <tr>
                <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">Data Processing</td>
                <td className="py-3 px-4 text-slate-500 dark:text-white/50">Reactive manual paper filing</td>
                <td className="py-3 px-4 text-emerald-600 dark:text-emerald-400 font-bold">Real-time GNN Graph Ingestion</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">Crime Analytics</td>
                <td className="py-3 px-4 text-slate-500 dark:text-white/50">Static monthly spreadsheets</td>
                <td className="py-3 px-4 text-emerald-600 dark:text-emerald-400 font-bold">48h Monte Carlo Threat Predictions</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-slate-900 dark:text-white">Copilot Interface</td>
                <td className="py-3 px-4 text-slate-500 dark:text-white/50">None (Keyword search only)</td>
                <td className="py-3 px-4 text-emerald-600 dark:text-emerald-400 font-bold">Natural Language Neural Copilot</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 9. Team Section */}
      <section id="team" className="relative z-10 max-w-6xl mx-auto px-6 py-16 space-y-8">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
            Engineering & Intelligence Architecture
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-white/50">
            Designed by senior product architects and AI researchers
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 sm:gap-6">
          {[
            {
              name: "Kamal Solanki",
              initials: "KS",
              role: "Team Lead • AI & Full Stack",
              desc: "Leading the overall product architecture, AI workflow, frontend-backend integration and project coordination.",
            },
            {
              name: "Muskan Yeshmin Ali",
              initials: "MY",
              role: "UI/UX Designer • Product Design",
              desc: "Responsible for UI/UX, visual design system, presentation assets and overall user experience.",
            },
            {
              name: "Saloni Nautiyal",
              initials: "SN",
              role: "Frontend Developer",
              desc: "Responsible for frontend implementation, responsive layouts and reusable UI components.",
            },
            {
              name: "Abhishek Chindaliya",
              initials: "AC",
              role: "Backend Developer",
              desc: "Responsible for backend APIs, database integration and server-side development.",
            },
            {
              name: "Siddhi Mittal",
              initials: "SM",
              role: "Research & Documentation",
              desc: "Responsible for research, documentation, testing and project coordination.",
            },
          ].map((t, idx) => (
            <div key={idx} className="p-5 rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 space-y-3.5 text-center shadow-sm flex flex-col justify-between hover:border-primary/40 transition-colors">
              <div className="space-y-3">
                <div className="h-14 w-14 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center font-bold text-white text-lg mx-auto shadow-lg tracking-wider font-mono">
                  {t.initials}
                </div>
                <div>
                  <h3 className="font-bold text-sm text-slate-900 dark:text-white leading-tight">{t.name}</h3>
                  <p className="text-[11px] font-semibold text-primary mt-1 leading-tight">{t.role}</p>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-white/60 leading-relaxed font-sans">{t.desc}</p>
              </div>
              <div className="pt-2.5 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-center text-[10px] font-mono">
                <span className="px-2 py-0.5 rounded bg-slate-100 dark:bg-white/[0.05] border border-slate-200 dark:border-white/10 text-slate-500 dark:text-white/40">CORE CONTRIBUTOR</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 10. FAQ Section */}
      <section id="faq" className="relative z-10 max-w-4xl mx-auto px-6 py-16 space-y-8">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white">Frequently Asked Questions</h2>
          <p className="text-xs text-slate-500 dark:text-white/50">Hackathon judging & compliance details</p>
        </div>

        <div className="space-y-3">
          {faqList.map((faq, idx) => (
            <div key={idx} className="rounded-2xl border border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 overflow-hidden shadow-sm">
              <button
                onClick={() => toggleFaq(idx)}
                className="w-full p-4 text-left font-bold text-xs sm:text-sm text-slate-900 dark:text-white flex items-center justify-between"
              >
                <span>{faq.q}</span>
                <ChevronDown className={`h-4 w-4 text-primary transition-transform ${openFaq === idx ? "rotate-180" : ""}`} />
              </button>
              {openFaq === idx && (
                <div className="px-4 pb-4 text-xs text-slate-600 dark:text-white/70 border-t border-slate-100 dark:border-white/[0.06] pt-3 leading-relaxed">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 11. CTA Banner */}
      <section className="relative z-10 max-w-5xl mx-auto px-6 py-16">
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-r from-primary via-blue-600 to-accent text-white text-center space-y-6 shadow-2xl relative overflow-hidden">
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight">Ready to Deploy Sentinel AI?</h2>
          <p className="text-xs sm:text-sm text-white/80 max-w-xl mx-auto leading-relaxed">
            Experience the future of law enforcement crime intelligence and decision operations today.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <Link
              href="/dashboard"
              className="w-full sm:w-auto px-8 py-3 bg-white text-slate-900 font-bold text-xs rounded-xl shadow-lg hover:bg-slate-100 transition-colors"
            >
              Launch Command Center
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto px-8 py-3 bg-slate-900/40 hover:bg-slate-900/60 text-white font-bold text-xs rounded-xl border border-white/20 transition-colors"
            >
              Officer Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* 12. Footer */}
      <footer className="relative z-10 border-t border-slate-200/80 dark:border-white/[0.08] py-12 px-6 bg-white/80 dark:bg-[#050816]/80 backdrop-blur-xl text-xs text-slate-500 dark:text-white/40">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 mb-8 text-left">
          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 dark:text-white uppercase font-mono text-[10px]">Sentinel AI</h4>
            <p className="text-[11px] leading-relaxed">AI Powered Crime Intelligence & Decision Operating System.</p>
          </div>
          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 dark:text-white uppercase font-mono text-[10px]">Modules</h4>
            <ul className="space-y-1 text-[11px]">
              <li><Link href="/dashboard" className="hover:text-primary">Command Center</Link></li>
              <li><Link href="/copilot" className="hover:text-primary">Security Copilot</Link></li>
              <li><Link href="/network-analysis" className="hover:text-primary">Network Intel</Link></li>
              <li><Link href="/simulation" className="hover:text-primary">Simulation Engine</Link></li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 dark:text-white uppercase font-mono text-[10px]">Legal & Compliance</h4>
            <ul className="space-y-1 text-[11px]">
              <li><Link href="#" className="hover:text-primary">FBI CJIS Level 5</Link></li>
              <li><Link href="#" className="hover:text-primary">Privacy Policy</Link></li>
              <li><Link href="#" className="hover:text-primary">Terms of Service</Link></li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-bold text-slate-900 dark:text-white uppercase font-mono text-[10px]">Connect</h4>
            <div className="flex items-center gap-3">
              <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-slate-900 dark:hover:text-white"><FaGithub className="h-4 w-4" /></a>
              <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="hover:text-primary"><FaLinkedin className="h-4 w-4" /></a>
              <a href="mailto:intel@sentinel-ai.gov" className="hover:text-accent"><Mail className="h-4 w-4" /></a>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-100 dark:border-white/[0.06] flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-[10px]">
          <span>© 2026 Sentinel AI Inc. Production-Grade Hackathon Enterprise Project.</span>
          <span className="flex items-center gap-1.5 text-emerald-500 font-bold">
            <ShieldCheck className="h-3.5 w-3.5" /> CJIS VERIFIED • LEVEL 5
          </span>
        </div>
      </footer>
    </div>
  );
}
