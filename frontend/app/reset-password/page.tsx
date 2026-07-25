"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  Lock,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Eye,
  EyeOff,
  KeyRound,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleReset = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) return;

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setSuccess(true);
      setTimeout(() => {
        router.push("/login");
      }, 1500);
    }, 1200);
  };

  return (
    <div className="min-h-screen w-full bg-slate-50 dark:bg-[#050816] flex items-center justify-center p-4 relative overflow-hidden text-slate-900 dark:text-white transition-colors duration-300">
      {/* Background Ambient Orbs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="orb absolute -top-40 -left-40 w-[600px] h-[600px] bg-primary/20" />
        <div className="orb absolute -bottom-40 -right-40 w-[500px] h-[500px] bg-accent/20" style={{ animationDelay: "-7s" }} />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Brand Header */}
        <div className="text-center space-y-2 mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-primary via-blue-500 to-accent text-white shadow-xl shadow-primary/30 mb-2">
            <KeyRound className="h-8 w-8" strokeWidth={2.2} />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white font-sans">
            SENTINEL AI
          </h1>
          <p className="text-xs text-slate-500 dark:text-white/40 uppercase tracking-[0.2em] font-mono">
            New Password Provisioning
          </p>
        </div>

        {/* Vessel Card */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-200/80 dark:border-white/[0.12] bg-white/90 dark:bg-[#0f172a]/80 backdrop-blur-2xl p-6 md:p-8 shadow-xl dark:shadow-2xl space-y-6"
        >
          {success ? (
            <div className="text-center space-y-4 py-4">
              <div className="h-16 w-16 rounded-2xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 flex items-center justify-center mx-auto shadow-lg">
                <CheckCircle2 className="h-8 w-8 text-emerald-500" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white font-mono">PASSWORD UPDATED</h3>
              <p className="text-xs text-slate-500 dark:text-white/50">Redirecting to login portal...</p>
            </div>
          ) : (
            <form onSubmit={handleReset} className="space-y-4 text-xs">
              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  New Encrypted Password
                </label>
                <div className="relative">
                  <Lock className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="••••••••••••"
                    className="w-full h-11 pl-9 pr-9 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs font-mono text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-white/30 hover:text-slate-700 dark:hover:text-white"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    placeholder="••••••••••••"
                    className="w-full h-11 pl-9 pr-3 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs font-mono text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full h-11 bg-gradient-to-r from-primary via-blue-600 to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-xl shadow-xl shadow-primary/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50 mt-2"
              >
                {isLoading ? (
                  <span className="font-mono animate-pulse">UPDATING PASSWORD...</span>
                ) : (
                  <>
                    <span>Reset Password & Sign In</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>
          )}
        </motion.div>

        {/* Compliance Footer */}
        <div className="text-center mt-6 text-[10px] font-mono text-slate-400 dark:text-white/30 space-y-1">
          <p className="flex items-center justify-center gap-1">
            <ShieldCheck className="h-3 w-3 text-emerald-500" /> CJIS COMPLIANT • 256-BIT ENCRYPTED
          </p>
          <p>© 2026 Sentinel AI Inc. Authorized Personnel Only.</p>
        </div>
      </div>
    </div>
  );
}
