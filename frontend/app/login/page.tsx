"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  Lock,
  User,
  ArrowRight,
  Fingerprint,
  Sparkles,
  ShieldCheck,
  KeyRound,
  Eye,
  EyeOff,
  Activity,
  CheckCircle2,
  Globe,
  Bot,
  Zap,
  Check,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

export default function LoginPage() {
  const router = useRouter();
  const [badgeNumber, setBadgeNumber] = useState("BADGE-88402");
  const [password, setPassword] = useState("••••••••••••");
  const [showPassword, setShowPassword] = useState(false);
  const [authMethod, setAuthMethod] = useState<"credentials" | "biometric" | "cac">("credentials");
  const [isLoading, setIsLoading] = useState(false);
  const [loginSuccess, setLoginSuccess] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setLoginSuccess(true);
      setTimeout(() => {
        router.push("/dashboard");
      }, 800);
    }, 1000);
  };

  const handleOAuthLogin = (provider: string) => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setLoginSuccess(true);
      setTimeout(() => {
        router.push("/dashboard");
      }, 800);
    }, 1000);
  };

  return (
    <div className="min-h-screen w-full bg-slate-50 dark:bg-[#050816] flex flex-col lg:flex-row text-slate-900 dark:text-white relative overflow-hidden transition-colors duration-300">
      {/* Left Column: Brand, Mission & System Telemetry Status (Hidden on Mobile) */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-slate-900 via-[#050816] to-[#0f172a] p-12 flex-col justify-between overflow-hidden border-r border-white/[0.08]">
        {/* Ambient Background Glow Orbs */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
          <div className="orb absolute -top-40 -left-40 w-[600px] h-[600px] bg-primary/20" />
          <div className="orb absolute bottom-0 right-0 w-[500px] h-[500px] bg-accent/20" style={{ animationDelay: "-7s" }} />
          <div className="cyber-grid absolute inset-0 opacity-20" />
        </div>

        {/* Top Brand Logo */}
        <div className="relative z-10 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-br from-primary via-blue-500 to-accent flex items-center justify-center shadow-lg shadow-primary/30 group-hover:scale-105 transition-transform">
              <ShieldAlert className="h-6 w-6 text-white" strokeWidth={2.2} />
            </div>
            <div>
              <span className="text-base font-extrabold tracking-tight text-white font-sans block">
                SENTINEL AI
              </span>
              <span className="text-[9px] font-mono text-white/40 uppercase tracking-[0.2em]">
                Law Enforcement OS
              </span>
            </div>
          </Link>

          <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            ENTERPRISE DEMO SESSION
          </span>
        </div>

        {/* Hero Mission & System Status Content */}
        <div className="relative z-10 space-y-6 max-w-lg my-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-xs font-mono text-primary font-bold">
            <Sparkles className="h-3.5 w-3.5 text-accent" />
            ENTERPRISE SECURITY CONSOLE PREVIEW
          </div>

          <h2 className="text-3xl lg:text-4xl font-extrabold tracking-tight text-white leading-tight">
            AI Powered Crime Intelligence & Decision Operating System
          </h2>

          <p className="text-sm text-white/60 leading-relaxed">
            Real-time crime prediction, criminal network graph analysis, Security Copilot reasoning, and Monte Carlo tactical simulation.
          </p>

          {/* Live System Metrics Card */}
          <div className="p-4 rounded-2xl bg-white/[0.03] border border-white/[0.08] backdrop-blur-xl grid grid-cols-3 gap-4 text-center font-mono">
            <div className="border-r border-white/[0.06] pr-2">
              <span className="text-[10px] text-white/40 block">ACCURACY</span>
              <span className="text-sm font-bold text-emerald-400">99.8%</span>
            </div>
            <div className="border-r border-white/[0.06] pr-2">
              <span className="text-[10px] text-white/40 block">ENTITIES</span>
              <span className="text-sm font-bold text-primary">1,204</span>
            </div>
            <div>
              <span className="text-[10px] text-white/40 block">LATENCY</span>
              <span className="text-sm font-bold text-accent">&lt;1.2s</span>
            </div>
          </div>

          {/* System Telemetry & Status Widget */}
          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-2.5 font-mono text-xs text-white/70">
            <span className="text-[10px] font-bold text-white/40 uppercase tracking-widest block mb-1">
              SYSTEM STATUS TELEMETRY
            </span>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Check className="h-3.5 w-3.5 text-emerald-400" /> Security Copilot Engine
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">ONLINE</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Check className="h-3.5 w-3.5 text-emerald-400" /> Intelligence Database
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">SYNCED</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Check className="h-3.5 w-3.5 text-emerald-400" /> Spatial Threat Heatmaps
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">ACTIVE</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Check className="h-3.5 w-3.5 text-primary" /> Demo Authentication Workflow
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-primary/10 text-primary font-bold">READY</span>
            </div>
          </div>
        </div>

        {/* Bottom Realistic Bar */}
        <div className="relative z-10 pt-6 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-white/40">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <span>ENTERPRISE SECURITY PREVIEW • DEMO CONSOLE</span>
          </div>
          <span>v4.2 PROD</span>
        </div>
      </div>

      {/* Right Column: Authentication Form */}
      <div className="flex-1 flex flex-col justify-between p-6 sm:p-12 lg:p-16 relative z-10 my-auto max-w-xl mx-auto w-full">
        {/* Mobile Header */}
        <div className="lg:hidden flex items-center justify-between mb-8">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <span className="font-extrabold text-sm text-slate-900 dark:text-white">SENTINEL AI</span>
          </Link>
          <Link href="/" className="text-xs text-primary font-semibold hover:underline">
            ← Home
          </Link>
        </div>

        {/* Main Form Card */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="space-y-1">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              Command Sign In
            </h1>
            <p className="text-xs text-slate-500 dark:text-white/40">
              Access verified officer intelligence dashboard and Copilot
            </p>
          </div>

          {/* Auth Method Selector */}
          <div className="grid grid-cols-3 gap-1 p-1 rounded-xl bg-slate-100 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.08] text-xs font-semibold">
            <button
              onClick={() => setAuthMethod("credentials")}
              className={`py-2 rounded-lg transition-all ${
                authMethod === "credentials"
                  ? "bg-primary text-white shadow"
                  : "text-slate-500 dark:text-white/40 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Badge Creds
            </button>
            <button
              onClick={() => setAuthMethod("biometric")}
              className={`py-2 rounded-lg transition-all ${
                authMethod === "biometric"
                  ? "bg-primary text-white shadow"
                  : "text-slate-500 dark:text-white/40 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Biometric
            </button>
            <button
              onClick={() => setAuthMethod("cac")}
              className={`py-2 rounded-lg transition-all ${
                authMethod === "cac"
                  ? "bg-primary text-white shadow"
                  : "text-slate-500 dark:text-white/40 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              CAC / PIV
            </button>
          </div>

          {loginSuccess && (
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 rounded-xl text-xs font-bold font-mono flex items-center gap-2"
            >
              <CheckCircle2 className="h-4 w-4" /> AUTHENTICATION SUCCESSFUL • REDIRECTING...
            </motion.div>
          )}

          {/* Credential Login Form */}
          {authMethod === "credentials" && (
            <form onSubmit={handleLogin} className="space-y-4 text-xs">
              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Officer Badge ID / Email
                </label>
                <div className="relative">
                  <User className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={badgeNumber}
                    onChange={(e) => setBadgeNumber(e.target.value)}
                    required
                    className="w-full h-11 pl-10 pr-3 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs font-mono text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="font-semibold text-slate-700 dark:text-white/70 uppercase tracking-wider text-[10px]">
                    Encrypted Security Password
                  </label>
                  <Link href="/forgot-password" className="text-primary hover:underline text-[11px]">
                    Forgot Password?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full h-11 pl-10 pr-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs font-mono text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 dark:text-white/30 hover:text-slate-700 dark:hover:text-white"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between text-[11px] pt-1">
                <label className="flex items-center gap-2 text-slate-600 dark:text-white/50 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded border-slate-300 dark:border-white/20 bg-slate-100 dark:bg-white/5 text-primary h-4 w-4" />
                  <span>Remember Session</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full h-11 bg-gradient-to-r from-primary via-blue-600 to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-xl shadow-xl shadow-primary/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50 mt-2"
              >
                {isLoading ? (
                  <span className="font-mono animate-pulse flex items-center gap-2">
                    <Activity className="h-4 w-4 animate-spin text-white" /> VERIFYING CREDENTIALS...
                  </span>
                ) : (
                  <>
                    <span>Authenticate Command Access</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>
          )}

          {authMethod === "biometric" && (
            <div className="py-6 text-center space-y-4">
              <div className="h-20 w-20 rounded-3xl bg-primary/10 border border-primary/30 flex items-center justify-center mx-auto text-primary animate-pulse shadow-lg shadow-primary/20">
                <Fingerprint className="h-10 w-10" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">Touch Biometric Scanner</h3>
                <p className="text-xs text-slate-500 dark:text-white/40 mt-1">Place verified officer thumbprint on sensor</p>
              </div>
              <button
                onClick={() => handleOAuthLogin("biometric")}
                className="w-full h-11 bg-primary text-white rounded-xl font-bold text-xs shadow-lg"
              >
                Simulate Biometric Scan Match
              </button>
            </div>
          )}

          {authMethod === "cac" && (
            <div className="py-6 text-center space-y-4">
              <div className="h-20 w-20 rounded-3xl bg-accent/10 border border-accent/30 flex items-center justify-center mx-auto text-accent shadow-lg shadow-accent/20">
                <KeyRound className="h-10 w-10" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">Smart Card / CAC Reader</h3>
                <p className="text-xs text-slate-500 dark:text-white/40 mt-1">Insert PIV smartcard into hardware slot</p>
              </div>
              <button
                onClick={() => handleOAuthLogin("cac")}
                className="w-full h-11 bg-accent text-white rounded-xl font-bold text-xs shadow-lg"
              >
                Authenticate Smartcard PIN
              </button>
            </div>
          )}

          {/* Social / SSO Triggers */}
          <div className="space-y-3 pt-4 border-t border-slate-100 dark:border-white/[0.06]">
            <div className="text-center text-[10px] font-mono text-slate-400 dark:text-white/30 uppercase tracking-wider">
              Or Sign In with Agency SSO (Enterprise Demo Access)
            </div>

            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleOAuthLogin("Google")}
                className="py-2.5 px-3 rounded-xl bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/80 border border-slate-200 dark:border-white/[0.08] text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                Google
              </button>
              <button
                type="button"
                onClick={() => handleOAuthLogin("Microsoft")}
                className="py-2.5 px-3 rounded-xl bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/80 border border-slate-200 dark:border-white/[0.08] text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                Microsoft
              </button>
              <button
                type="button"
                onClick={() => handleOAuthLogin("GitHub")}
                className="py-2.5 px-3 rounded-xl bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/80 border border-slate-200 dark:border-white/[0.08] text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                GitHub
              </button>
            </div>
          </div>

          {/* Register Link */}
          <div className="text-center pt-2 text-xs">
            <span className="text-slate-500 dark:text-white/40">Don&apos;t have clearance yet? </span>
            <Link href="/signup" className="text-primary font-bold hover:underline">
              Request Officer Account
            </Link>
          </div>
        </motion.div>

        {/* Footer */}
        <div className="mt-8 text-center text-[10px] font-mono text-slate-400 dark:text-white/30 space-y-1">
          <p className="flex items-center justify-center gap-1">
            <ShieldCheck className="h-3 w-3 text-emerald-500" /> PROTOTYPE AUTHENTICATION ENVIRONMENT • READY FOR IDP INTEGRATION
          </p>
          <p>© 2026 Sentinel AI Inc. Authorized Personnel Only.</p>
        </div>
      </div>
    </div>
  );
}
