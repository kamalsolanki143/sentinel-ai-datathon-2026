"use client";

import React from "react";

interface LoadingSkeletonProps {
  type?: "card" | "table" | "list" | "chart";
  count?: number;
}

export default function LoadingSkeleton({ type = "card", count = 3 }: LoadingSkeletonProps) {
  return (
    <div className="w-full space-y-3 animate-pulse">
      {type === "card" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: count }).map((_, idx) => (
            <div key={idx} className="h-28 rounded-xl border border-border bg-card/40 p-4 space-y-3">
              <div className="h-4 bg-muted/60 rounded w-1/3" />
              <div className="h-7 bg-muted/80 rounded w-1/2" />
              <div className="h-3 bg-muted/40 rounded w-2/3" />
            </div>
          ))}
        </div>
      )}

      {type === "table" && (
        <div className="rounded-xl border border-border bg-card/40 overflow-hidden">
          <div className="h-10 bg-muted/40 border-b border-border" />
          <div className="p-4 space-y-3">
            {Array.from({ length: count }).map((_, idx) => (
              <div key={idx} className="flex justify-between items-center gap-4">
                <div className="h-4 bg-muted/60 rounded w-1/4" />
                <div className="h-4 bg-muted/40 rounded w-1/3" />
                <div className="h-4 bg-muted/50 rounded w-1/6" />
                <div className="h-6 bg-muted/60 rounded w-12" />
              </div>
            ))}
          </div>
        </div>
      )}

      {type === "chart" && (
        <div className="h-64 rounded-xl border border-border bg-card/40 p-4 flex flex-col justify-between">
          <div className="h-4 bg-muted/60 rounded w-1/4" />
          <div className="h-40 bg-muted/20 rounded w-full flex items-end justify-between px-4 pb-2">
            <div className="h-20 w-8 bg-muted/50 rounded" />
            <div className="h-32 w-8 bg-muted/60 rounded" />
            <div className="h-28 w-8 bg-muted/50 rounded" />
            <div className="h-36 w-8 bg-muted/70 rounded" />
          </div>
        </div>
      )}
    </div>
  );
}
