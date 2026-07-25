"use client";

import React from "react";
import { motion } from "framer-motion";

interface SectionCardProps {
  title: string;
  subtitle?: string;
  icon?: React.ElementType;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "glass" | "bordered" | "danger";
}

export default function SectionCard({
  title,
  subtitle,
  icon: Icon,
  action,
  children,
  className = "",
  variant = "glass",
}: SectionCardProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case "danger":
        return "border-red-500/30 bg-red-500/5";
      case "bordered":
        return "border-slate-300 dark:border-white/[0.12] bg-white dark:bg-[#0f172a]/80 shadow-md";
      case "default":
        return "border-slate-200 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/90";
      case "glass":
      default:
        return "border-slate-200/80 dark:border-white/[0.08] bg-white/90 dark:bg-[#0f172a]/60 backdrop-blur-xl shadow-sm dark:shadow-xl";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`rounded-2xl border p-5 ${getVariantStyles()} ${className} transition-colors duration-300`}
    >
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3.5 mb-4">
        <div className="flex items-center gap-2.5">
          {Icon && (
            <div className="p-2 rounded-xl bg-primary/10 text-primary border border-primary/20">
              <Icon className="h-4 w-4" />
            </div>
          )}
          <div>
            <h3 className="font-bold text-sm text-slate-900 dark:text-white tracking-wide">{title}</h3>
            {subtitle && <p className="text-xs text-slate-500 dark:text-white/40 mt-0.5">{subtitle}</p>}
          </div>
        </div>
        {action && <div>{action}</div>}
      </div>

      <div>{children}</div>
    </motion.div>
  );
}
