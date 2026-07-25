"use client";

import React from "react";
import { motion } from "framer-motion";

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  hoverScale?: boolean;
}

export default function AnimatedCard({
  children,
  className = "",
  delay = 0,
  hoverScale = true,
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={hoverScale ? { y: -2, transition: { duration: 0.2 } } : undefined}
      className={`rounded-xl border border-border bg-card/60 backdrop-blur-md shadow-sm transition-shadow hover:shadow-md ${className}`}
    >
      {children}
    </motion.div>
  );
}
