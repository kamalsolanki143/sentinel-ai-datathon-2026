"use client";

import React, { useState } from "react";
import {
  ShieldAlert,
  Lock,
  User,
  ArrowRight,
  ShieldCheck,
  Mail,
  BadgeCheck,
  Building2,
  CheckCircle2,
  Eye,
  EyeOff,
  Activity,
  Sparkles,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function SignupPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [badgeNumber, setBadgeNumber] = useState("");
  const [organization, setOrganization] = useState("Metropolitan Police Department");
  const [role, setRole] = useState("Police Officer");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const getPasswordStrength = () => {
    if (!password) return { score: 0, label: "Empty", color: "bg-slate-200 dark:bg-white/10" };
    if (password.length < 6) return { score: 1, label: "Weak", color: "bg-red-500" };
    if (password.length < 10) return { score: 2, label: "Medium", color: "bg-amber-500" };
    if (/[A-Z]/.test(password) && /[0-9]/.test(password) && /[^A-Za-z0-9]/.test(password)) {
      return { score: 4, label: "Strong (L5)", color: "bg-emerald-500" };
    }
    return { score: 3, label: "Good", color: "bg-primary" };
  };

  const strength = getPasswordStrength();

  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (password !== confirmPassword) {
      setErrorMsg("Security passwords do not match.");
      return;
    }

    if (!agreeTerms) {
      setErrorMsg("You must accept CJIS Security Directives.");
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setSuccess(true);
      setTimeout(() => {
        router.push("/verify-email");
      }, 1200);
    }, 1200);
  };

  return (
    <div className="min-h-screen w-full bg-slate-50 dark:bg-[#050816] flex flex-col lg:flex-row text-slate-900 dark:text-white relative overflow-hidden transition-colors duration-300">
      {/* Left Column: Brand & Role System */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-slate-900 via-[#050816] to-[#0f172a] p-12 flex-col justify-between overflow-hidden border-r border-white/[0.08]">
        {/* Background Ambient */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
          <div className="orb absolute -top-40 -left-40 w-[600px] h-[600px] bg-accent/20" />
          <div className="orb absolute bottom-0 right-0 w-[500px] h-[500px] bg-primary/20" style={{ animationDelay: "-7s" }} />
          <div className="dot-grid absolute inset-0 opacity-20" />
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
                Personnel Onboarding
              </span>
            </div>
          </Link>

          <span className="text-[10px] font-mono font-bold px-2.5 py-1 rounded-full bg-primary/10 text-primary border border-primary/20">
            OFFICER CLEARANCE SYSTEM
          </span>
        </div>

        {/* Role System Information Card */}
        <div className="relative z-10 space-y-6 max-w-lg my-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20 text-xs font-mono text-accent font-bold">
            <Sparkles className="h-3.5 w-3.5" />
            MULTI-ROLE LAW ENFORCEMENT ARCHITECTURE
          </div>

          <h2 className="text-3xl font-extrabold tracking-tight text-white leading-tight">
            Role-Based Security & Access Control
          </h2>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/20 text-primary shrink-0 font-bold font-mono">ADM</div>
              <div>
                <h4 className="font-bold text-white">Administrator</h4>
                <p className="text-white/50 text-[11px] mt-0.5">Full system management, API configuration, and user clearance granting.</p>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-start gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400 shrink-0 font-bold font-mono">OFF</div>
              <div>
                <h4 className="font-bold text-white">Police Officer</h4>
                <p className="text-white/50 text-[11px] mt-0.5">Real-time incident stream, spatial dispatch, and patrol telemetry.</p>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-start gap-3">
              <div className="p-2 rounded-lg bg-accent/20 text-accent shrink-0 font-bold font-mono">ANA</div>
              <div>
                <h4 className="font-bold text-white">Crime Analyst</h4>
                <p className="text-white/50 text-[11px] mt-0.5">Monte Carlo crime prediction, syndicate network graph, and AI report synthesis.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Compliance Bar */}
        <div className="relative z-10 pt-6 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-white/40">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <span>ENCRYPTED ACCOUNT PROVISIONING</span>
          </div>
          <span>VERIFICATION REQUIRED</span>
        </div>
      </div>

      {/* Right Column: Registration Form */}
      <div className="flex-1 flex flex-col justify-between p-6 sm:p-12 lg:p-16 relative z-10 max-w-xl mx-auto w-full my-auto">
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <div className="space-y-1">
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
              Request Officer Clearance
            </h1>
            <p className="text-xs text-slate-500 dark:text-white/40">
              Provision agency account for Sentinel AI Operating System
            </p>
          </div>

          {errorMsg && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 text-red-500 dark:text-red-400 rounded-xl text-xs font-semibold">
              {errorMsg}
            </div>
          )}

          {success && (
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 rounded-xl text-xs font-bold font-mono flex items-center gap-2"
            >
              <CheckCircle2 className="h-4 w-4" /> ACCOUNT PROVISIONED • DISPATCHING OTP...
            </motion.div>
          )}

          <form onSubmit={handleSignup} className="space-y-3.5 text-xs">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Full Name
                </label>
                <div className="relative">
                  <User className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Officer Jane Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    className="w-full h-10 pl-9 pr-3 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Official Agency Email
                </label>
                <div className="relative">
                  <Mail className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="email"
                    placeholder="jane.doe@pd.gov"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full h-10 pl-9 pr-3 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Badge Identifier
                </label>
                <div className="relative">
                  <BadgeCheck className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="BADGE-99401"
                    value={badgeNumber}
                    onChange={(e) => setBadgeNumber(e.target.value)}
                    required
                    className="w-full h-10 pl-9 pr-3 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs font-mono text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Assigned Security Role
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full h-10 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-[#050816] px-3 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                >
                  <option value="Police Officer">Police Officer</option>
                  <option value="Crime Analyst">Crime Analyst</option>
                  <option value="Investigator">Investigator / Detective</option>
                  <option value="Administrator">Administrator</option>
                </select>
              </div>
            </div>

            <div>
              <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                Law Enforcement Department / Agency
              </label>
              <div className="relative">
                <Building2 className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  required
                  className="w-full h-10 pl-9 pr-3 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="font-semibold text-slate-700 dark:text-white/70 block mb-1 uppercase tracking-wider text-[10px]">
                  Security Password
                </label>
                <div className="relative">
                  <Lock className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full h-10 pl-9 pr-9 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs font-mono text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
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
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="h-4 w-4 text-slate-400 dark:text-white/30 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="w-full h-10 pl-9 pr-3 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-[#050816] text-xs font-mono text-slate-900 dark:text-white focus:outline-none focus:border-primary/50 transition-all"
                  />
                </div>
              </div>
            </div>

            {/* Password Strength Indicator */}
            {password && (
              <div className="space-y-1 pt-1">
                <div className="flex justify-between items-center text-[10px] font-mono">
                  <span className="text-slate-500 dark:text-white/40">PASSWORD STRENGTH:</span>
                  <span className="font-bold">{strength.label}</span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-white/10 h-1.5 rounded-full overflow-hidden">
                  <div className={`h-full transition-all duration-300 ${strength.color}`} style={{ width: `${(strength.score / 4) * 100}%` }} />
                </div>
              </div>
            )}

            {/* CJIS Terms Agreement */}
            <div className="pt-2">
              <label className="flex items-start gap-2 text-slate-600 dark:text-white/60 text-[11px] cursor-pointer">
                <input
                  type="checkbox"
                  checked={agreeTerms}
                  onChange={(e) => setAgreeTerms(e.target.checked)}
                  className="rounded border-slate-300 dark:border-white/20 bg-slate-100 dark:bg-white/5 text-primary h-4 w-4 mt-0.5"
                />
                <span>I agree to CJIS Security Directives and law enforcement audit protocols.</span>
              </label>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-11 bg-gradient-to-r from-primary via-blue-600 to-accent hover:from-primary/90 hover:to-accent/90 text-white font-bold text-xs rounded-xl shadow-xl shadow-primary/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50 mt-3"
            >
              {isLoading ? (
                <span className="font-mono animate-pulse flex items-center gap-2">
                  <Activity className="h-4 w-4 animate-spin text-white" /> PROVISIONING ACCOUNT...
                </span>
              ) : (
                <>
                  <span>Submit Account Request</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          <div className="text-center pt-2 text-xs">
            <span className="text-slate-500 dark:text-white/40">Already registered? </span>
            <Link href="/login" className="text-primary font-bold hover:underline">
              Sign In Here
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
