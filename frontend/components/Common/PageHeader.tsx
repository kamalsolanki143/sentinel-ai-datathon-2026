"use client";

import React from "react";
import Link from "next/link";
import { ChevronRight, Shield } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: BreadcrumbItem[];
  icon?: React.ElementType;
  statusBadge?: React.ReactNode;
  children?: React.ReactNode;
}

export default function PageHeader({
  title,
  subtitle,
  breadcrumbs = [{ label: "Command Center", href: "/dashboard" }],
  icon: Icon = Shield,
  statusBadge,
  children,
}: PageHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200/80 dark:border-white/[0.08] mb-6">
      <div className="space-y-1.5">
        {/* Breadcrumb Navigation */}
        <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-white/40 font-mono">
          {breadcrumbs.map((item, idx) => (
            <React.Fragment key={idx}>
              {idx > 0 && <ChevronRight className="h-3 w-3 text-slate-300 dark:text-white/20" />}
              {item.href ? (
                <Link href={item.href} className="hover:text-primary transition-colors">
                  {item.label}
                </Link>
              ) : (
                <span className="text-slate-800 dark:text-white/80 font-bold">{item.label}</span>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Title and Icon */}
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-primary/10 border border-primary/20 text-primary shadow-lg shadow-primary/10">
            <Icon className="h-6 w-6" strokeWidth={2.2} />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                {title}
              </h1>
              {statusBadge}
            </div>
            {subtitle && (
              <p className="text-xs text-slate-500 dark:text-white/40 mt-0.5 max-w-2xl">{subtitle}</p>
            )}
          </div>
        </div>
      </div>

      {children && (
        <div className="flex items-center gap-2 shrink-0">{children}</div>
      )}
    </div>
  );
}
