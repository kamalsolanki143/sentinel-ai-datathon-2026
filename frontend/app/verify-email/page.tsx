"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  ShieldAlert,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  MailCheck,
  RotateCcw,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function VerifyEmailPage() {
  const router = useRouter();
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [verified, setVerified] = useState(false);
  const [resendTimer, setResendTimer] = useState(30);

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (resendTimer > 0) {
      const timer = setInterval(() => setResendTimer((t) => t - 1), 1000);
      return () => clearInterval(timer);
    }
  }, [resendTimer]);

  const handleChange = (index: number, value: string) => {
    if (value.length > 1) value = value.slice(-1);
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleVerify = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setVerified(true);
      setTimeout(() => {
        router.push("/dashboard");
      }, 1000);
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
            <MailCheck className="h-8 w-8" strokeWidth={2.2} />
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white font-sans">
            SENTINEL AI
          </h1>
          <p className="text-xs text-slate-500 dark:text-white/40 uppercase tracking-[0.2em] font-mono">
            6-Digit Verification Protocol
          </p>
        </div>

        {/* Vessel Card */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-3xl border border-slate-200/80 dark:border-white/[0.12] bg-white/90 dark:bg-[#0f172a]/80 backdrop-blur-2xl p-6 md:p-8 shadow-xl dark:shadow-2xl space-y-6 text-center"
        >
          {verified ? (
            <div className="space-y-4 py-4">
              <div className="h-16 w-16 rounded-2xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 flex items-center justify-center mx-auto shadow-lg">
                <CheckCircle2 className="h-8 w-8 text-emerald-500" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white font-mono">CLEARANCE VERIFIED</h3>
              <p className="text-xs text-slate-500 dark:text-white/50">Redirecting to Sentinel Command Center...</p>
            </div>
          ) : (
            <form onSubmit={handleVerify} className="space-y-6">
              <div className="space-y-1">
                <h3 className="font-bold text-base text-slate-900 dark:text-white">Enter Security Token</h3>
                <p className="text-xs text-slate-500 dark:text-white/40 leading-relaxed">
                  We&apos;ve sent a 6-digit OTP code to your official agency email address.
                </p>
              </div>

              {/* 6 Inputs */}
              <div className="flex justify-center items-center gap-2">
                {otp.map((digit, idx) => (
                  <input
                    key={idx}
                    ref={(el) => { inputRefs.current[idx] = el; }}
                    type="text"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleChange(idx, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(idx, e)}
                    className="w-11 h-12 text-center text-lg font-bold font-mono rounded-xl border border-slate-200 dark:border-white/[0.1] bg-slate-50 dark:bg-[#050816] text-slate-900 dark:text-white focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/30 transition-all"
                  />
                ))}
              </div>

              <button
                type="submit"
                disabled={isLoading || otp.some((d) => !d)}
                className="w-full h-11 bg-gradient-to-r from-primary via-blue-600 to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-xl shadow-xl shadow-primary/25 flex items-center justify-center gap-2 transition-all disabled:opacity-40"
              >
                {isLoading ? (
                  <span className="font-mono animate-pulse">VERIFYING OTP TOKEN...</span>
                ) : (
                  <>
                    <span>Verify Code & Continue</span>
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>

              <div className="text-center pt-2 text-xs font-mono text-slate-500 dark:text-white/40">
                {resendTimer > 0 ? (
                  <span>Resend Code in {resendTimer}s</span>
                ) : (
                  <button
                    type="button"
                    onClick={() => setResendTimer(30)}
                    className="text-primary font-bold hover:underline flex items-center justify-center gap-1 mx-auto"
                  >
                    <RotateCcw className="h-3.5 w-3.5" /> Resend Security Token
                  </button>
                )}
              </div>
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
