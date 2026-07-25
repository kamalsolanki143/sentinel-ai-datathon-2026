"use client";

import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { ShieldAlert, MapPin, Radio, Activity, Sparkles, Navigation } from "lucide-react";
import { useTheme } from "@/components/Theme/ThemeProvider";

const crimeData = [
  { id: 1, lat: 40.7128, lng: -74.0060, intensity: 0.94, type: "Armed Vault Intrusion", location: "Downtown Sector 4", priority: "CRITICAL" },
  { id: 2, lat: 40.7282, lng: -73.7949, intensity: 0.42, type: "Identity Theft Ring", location: "Sector 1 Commercial", priority: "MEDIUM" },
  { id: 3, lat: 40.7589, lng: -73.9851, intensity: 0.88, type: "Cargo Smuggling", location: "Sector 2 Port & Harbor", priority: "HIGH" },
  { id: 4, lat: 40.6782, lng: -73.9442, intensity: 0.65, type: "Commercial Burglary", location: "Sector 3 Suburbs", priority: "HIGH" },
  { id: 5, lat: 40.7306, lng: -73.9352, intensity: 0.51, type: "Substation Vandalism", location: "Sector 4 Downtown", priority: "MEDIUM" },
  { id: 6, lat: 40.7831, lng: -73.9712, intensity: 0.35, type: "Vehicle Grand Theft", location: "Uptown Sector 5", priority: "LOW" },
  { id: 7, lat: 40.6500, lng: -73.9499, intensity: 0.76, type: "Gang Violence Escalation", location: "South Sector 2", priority: "CRITICAL" },
];

const getIntensityColor = (intensity: number) => {
  if (intensity > 0.75) return "#ef4444";
  if (intensity > 0.5) return "#f59e0b";
  return "#3b82f6";
};

interface HeatMapProps {
  height?: string | number;
}

export default function HeatMap({ height }: HeatMapProps = {}) {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div 
        className="w-full h-full bg-slate-100 dark:bg-[#050816] animate-pulse rounded-2xl flex items-center justify-center border border-slate-200 dark:border-white/[0.08]"
        style={height ? { height } : undefined}
      >
        <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-white/50 font-mono">
          <Activity className="h-4 w-4 animate-spin text-primary" />
          <span>INITIALIZING SPATIAL GEOLOCATION RADAR...</span>
        </div>
      </div>
    );
  }

  const tileUrl =
    theme === "dark"
      ? "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      : "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";

  return (
    <div 
      className="w-full h-full rounded-2xl overflow-hidden border border-slate-200/80 dark:border-white/[0.08] relative z-0 shadow-md dark:shadow-2xl group transition-colors duration-300"
      style={height ? { height } : undefined}
    >
      <MapContainer 
        center={[40.7250, -73.9600]} 
        zoom={11} 
        scrollWheelZoom={true}
        className="w-full h-full"
        style={{ background: theme === "dark" ? "#050816" : "#f8fafc" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url={tileUrl}
        />
        {crimeData.map((crime) => (
          <CircleMarker
            key={crime.id}
            center={[crime.lat, crime.lng]}
            radius={crime.intensity * 22}
            pathOptions={{
              fillColor: getIntensityColor(crime.intensity),
              color: getIntensityColor(crime.intensity),
              weight: 2,
              opacity: 0.9,
              fillOpacity: 0.45,
            }}
          >
            <Popup className="custom-leaflet-popup">
              <div className="p-2 space-y-2 min-w-[200px]">
                <div className="flex items-center justify-between border-b border-slate-200 dark:border-white/10 pb-1.5">
                  <span className="text-[10px] font-mono font-bold text-red-500 dark:text-red-400 flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3" /> {crime.priority}
                  </span>
                  <span className="text-[9px] font-mono text-slate-500 dark:text-white/40">RISK: {(crime.intensity * 100).toFixed(0)}%</span>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 dark:text-white">{crime.type}</h4>
                  <p className="text-[10px] text-slate-500 dark:text-white/60 flex items-center gap-1 mt-0.5">
                    <MapPin className="h-3 w-3 text-primary" /> {crime.location}
                  </p>
                </div>
                <button
                  onClick={() => alert(`Patrol Unit Dispatched to ${crime.location}`)}
                  className="w-full py-1 rounded bg-primary/20 hover:bg-primary text-primary hover:text-white text-[10px] font-bold tracking-wider transition-colors flex items-center justify-center gap-1"
                >
                  <Navigation className="h-2.5 w-2.5" /> DISPATCH UNIT
                </button>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      {/* Floating Legend Overlay Card */}
      <div className="absolute top-4 right-4 z-[400] bg-white/90 dark:bg-[#0f172a]/90 backdrop-blur-xl p-3.5 rounded-2xl border border-slate-200 dark:border-white/[0.12] shadow-xl dark:shadow-2xl space-y-2.5 text-xs">
        <div className="flex items-center justify-between gap-3 border-b border-slate-200 dark:border-white/[0.08] pb-2">
          <div className="flex items-center gap-2">
            <Radio className="h-3.5 w-3.5 text-primary animate-pulse" />
            <span className="font-bold text-slate-900 dark:text-white text-[11px] uppercase tracking-wider">Spatial Threat Matrix</span>
          </div>
        </div>

        <div className="space-y-1.5 text-[11px]">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-red-500 shadow-sm shadow-red-500/50" />
              <span className="text-slate-700 dark:text-white/70">Critical Risk Zone</span>
            </div>
            <span className="font-mono text-red-500 dark:text-red-400 font-bold text-[10px]">&gt;75%</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50" />
              <span className="text-slate-700 dark:text-white/70">Elevated Warning</span>
            </div>
            <span className="font-mono text-amber-500 dark:text-amber-400 font-bold text-[10px]">50-75%</span>
          </div>
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-primary shadow-sm shadow-primary/50" />
              <span className="text-slate-700 dark:text-white/70">Monitored Baseline</span>
            </div>
            <span className="font-mono text-primary font-bold text-[10px]">&lt;50%</span>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-200 dark:border-white/[0.08] flex items-center justify-between text-[9px] text-slate-400 dark:text-white/40 font-mono">
          <span>7 ACTIVE CLUSTERS</span>
          <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
            <Sparkles className="h-2.5 w-2.5" /> LIVE FEED
          </span>
        </div>
      </div>
    </div>
  );
}
