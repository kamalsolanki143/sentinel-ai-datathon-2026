"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

const authRoutes = ["/", "/login", "/signup", "/forgot-password", "/verify-email", "/reset-password"];

export default function MainContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAuthRoute = authRoutes.some(
    (route) => pathname === route || (route !== "/" && pathname.startsWith(route))
  );

  if (isAuthRoute) {
    return (
      <main className="flex-1 min-h-screen bg-slate-50 dark:bg-[#050816] transition-colors duration-300">
        {children}
      </main>
    );
  }

  return (
    <main className="flex-1 overflow-y-auto md:ml-[260px] dot-grid min-h-[calc(100vh-56px)] bg-slate-50 dark:bg-[#050816] text-slate-900 dark:text-[#f8fafc] p-4 md:p-6 lg:p-8 transition-colors duration-300">
      <AnimatePresence mode="wait">
        <motion.div
          key={pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
          className="w-full max-w-7xl mx-auto space-y-6"
        >
          {children}
        </motion.div>
      </AnimatePresence>
    </main>
  );
}
