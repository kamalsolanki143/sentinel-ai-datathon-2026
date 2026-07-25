"use client";

import React from "react";
import { AlertTriangle, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message?: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "warning" | "info";
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({
  isOpen,
  title,
  message,
  description,
  confirmText = "Confirm Action",
  cancelText = "Cancel",
  variant = "danger",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const contentText = description || message || "";

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 dark:bg-[#050816]/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.96 }}
          className="bg-white dark:bg-[#0f172a]/95 border border-slate-200 dark:border-white/[0.12] w-full max-w-md rounded-2xl shadow-2xl p-6 space-y-4"
        >
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div
                className={`p-2.5 rounded-xl border ${
                  variant === "danger"
                    ? "bg-red-500/10 border-red-500/30 text-red-500 dark:text-red-400"
                    : "bg-amber-500/10 border-amber-500/30 text-amber-500 dark:text-amber-400"
                }`}
              >
                <AlertTriangle className="h-5 w-5" />
              </div>
              <h3 className="font-bold text-sm text-slate-900 dark:text-white">{title}</h3>
            </div>
            <button
              onClick={onCancel}
              className="text-slate-400 hover:text-slate-700 dark:text-white/40 dark:hover:text-white p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-white/[0.06] transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <p className="text-xs text-slate-600 dark:text-white/70 leading-relaxed bg-slate-50 dark:bg-white/[0.02] p-3 rounded-xl border border-slate-200 dark:border-white/[0.04]">
            {contentText}
          </p>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              onClick={onCancel}
              className="px-4 py-2 bg-slate-100 dark:bg-white/[0.04] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-700 dark:text-white/70 hover:text-slate-900 dark:hover:text-white rounded-xl text-xs font-semibold border border-slate-200 dark:border-white/[0.08] transition-colors"
            >
              {cancelText}
            </button>
            <button
              onClick={onConfirm}
              className={`px-4 py-2 rounded-xl text-xs font-bold text-white shadow-lg transition-all ${
                variant === "danger"
                  ? "bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-600/90 hover:to-rose-600/90 shadow-red-600/20"
                  : "bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 shadow-primary/20"
              }`}
            >
              {confirmText}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
