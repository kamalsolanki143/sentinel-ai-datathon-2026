import React from "react";
import { TrendingUp, TrendingDown, LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend: "up" | "down" | "neutral";
  trendValue: string;
  description?: string;
  variant?: "default" | "danger" | "warning" | "success";
}

export default function MetricCard({
  title,
  value,
  icon: Icon,
  trend,
  trendValue,
  description,
  variant = "default",
}: MetricCardProps) {
  const getTrendColor = () => {
    if (trend === "up") return "text-destructive"; // For crime, up is usually bad
    if (trend === "down") return "text-success";
    return "text-muted-foreground";
  };

  const getVariantStyles = () => {
    switch (variant) {
      case "danger":
        return "border-destructive/50 bg-destructive/5";
      case "warning":
        return "border-warning/50 bg-warning/5";
      case "success":
        return "border-success/50 bg-success/5";
      default:
        return "border-border bg-card";
    }
  };

  return (
    <div className={`rounded-xl border p-6 shadow-sm transition-all hover:shadow-md ${getVariantStyles()}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-muted-foreground tracking-tight">
          {title}
        </h3>
        <div className={`p-2 rounded-lg ${
          variant === "default" ? "bg-primary/10 text-primary" : ""
        } ${
          variant === "danger" ? "bg-destructive/10 text-destructive" : ""
        } ${
          variant === "warning" ? "bg-warning/10 text-warning" : ""
        } ${
          variant === "success" ? "bg-success/10 text-success" : ""
        }`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      
      <div className="flex flex-col gap-1">
        <div className="text-3xl font-bold tracking-tight text-foreground">
          {value}
        </div>
        
        <div className="flex items-center gap-2 text-xs">
          <span className={`flex items-center font-medium ${getTrendColor()}`}>
            {trend === "up" && <TrendingUp className="h-3 w-3 mr-1" />}
            {trend === "down" && <TrendingDown className="h-3 w-3 mr-1" />}
            {trendValue}
          </span>
          <span className="text-muted-foreground">{description || "vs last month"}</span>
        </div>
      </div>
    </div>
  );
}
