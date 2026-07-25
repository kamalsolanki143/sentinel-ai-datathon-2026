"use client";

import React from "react";
import { ShieldAlert, RefreshCw } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ElementType;
  onRetry?: () => void;
  actionText?: string;
}

export default function EmptyState({
  title = "No Data Found",
  description = "No matching intelligence records were found for the current query parameters.",
  icon: Icon = ShieldAlert,
  onRetry,
  actionText = "Reset Query",
}: EmptyStateProps) {
  return (
    <div className="w-full p-8 rounded-xl border border-dashed border-border/80 bg-card/40 backdrop-blur-sm flex flex-col items-center justify-center text-center space-y-3">
      <div className="p-3 rounded-full bg-primary/10 text-primary border border-primary/20">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="font-semibold text-sm text-foreground">{title}</h3>
      <p className="text-xs text-muted-foreground max-w-sm leading-relaxed">{description}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 px-3 py-1.5 bg-secondary hover:bg-secondary/80 text-foreground border border-border rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          {actionText}
        </button>
      )}
    </div>
  );
}
