"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  Mail,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setSubmitted(true);
    }, 1000);
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
            <ShieldAlert className="h-8 w-8" strokeWidth={2.2} />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white font-sans">
            SENTINEL AI
          </h1>
          <p className="text-xs text-slate-500 dark:text-white/40 uppercase tracking-[0.2em] font-mono">
            Password & Access Recovery Protocol
          </p>
        </div>

        {/* Vessel Card */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-200/80 dark:border-white/[0.12] bg-white/90 dark:bg-[#0f172a]/80 backdrop-blur-2xl p-6 md:p-8 shadow-xl dark:shadow-2xl space-y-6"
        >
          {submitted ? (
            <div className="text-center space-y-4 py-4">
              <div className="h-14 w-14 rounded-2xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 flex items-center justify-center mx-auto shadow-lg">
                <CheckCircle2 className="h-8 w-8" />
              </div>
              <div>
                <h3 className="font-bold text-sm text-slate-900 dark:text-white">Recovery Instructions Sent</h3>
                <p className="text-xs text-slate-500 dark:text-white/50 mt-1 leading-relaxed">
                  An encrypted access reset link has been dispatched to <strong>{email}</strong>.
                </p>
              </div>
              <Link
                href="/login"
                className="inline-block w-full py-2.5 bg-primary text-white rounded-xl font-bold text-xs shadow-lg"
              >
                Return to Command Sign In
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Registered Agency Email
                </label>
                <div className="relative">
                  <Mail className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    placeholder="officer@pd.gov"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full h-10 pl-9 pr-3 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-gradient-to-r from-primary via-blue-600 to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-xl shadow-xl shadow-primary/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50 mt-2"
              >
                {isLoading ? (
                  <span className="font-mono animate-pulse">DISPATCHING RESET LINK...</span>
                ) : (
                  <>
                    <span>Dispatch Recovery Protocol</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>

              <div className="text-center pt-2 border-t border-slate-100 dark:border-white/[0.06] text-xs">
                <Link href="/login" className="text-slate-500 dark:text-white/50 hover:text-slate-900 dark:hover:text-white font-medium">
                  ← Back to Sign In
                </Link>
              </div>
            </form>
          )}
        </motion.div>

        {/* Compliance Footer */}
        <div className="text-center mt-6 text-[10px] font-mono text-slate-400 dark:text-white/30 space-y-1">
          <p className="flex items-center justify-center gap-1">
            <ShieldCheck className="h-3 w-3 text-emerald-500" /> CJIS COMPLIANT • 256-BIT ENCRYPTED
          </p>
          <p>© 2026 Sentinel AI Inc. Authorized Law Enforcement Personnel Only.</p>
        </div>
      </div>
    </div>
  );
}
