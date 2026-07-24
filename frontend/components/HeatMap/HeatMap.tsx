"use client";

import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Mock crime data for heatmap
const crimeData = [
  { id: 1, lat: 40.7128, lng: -74.0060, intensity: 0.8, type: "Assault" },
  { id: 2, lat: 40.7282, lng: -73.7949, intensity: 0.4, type: "Theft" },
  { id: 3, lat: 40.7589, lng: -73.9851, intensity: 0.9, type: "Robbery" },
  { id: 4, lat: 40.6782, lng: -73.9442, intensity: 0.6, type: "Burglary" },
  { id: 5, lat: 40.7306, lng: -73.9352, intensity: 0.5, type: "Vandalism" },
  { id: 6, lat: 40.7831, lng: -73.9712, intensity: 0.2, type: "Theft" },
  { id: 7, lat: 40.6500, lng: -73.9499, intensity: 0.7, type: "Assault" },
];

const getIntensityColor = (intensity: number) => {
  if (intensity > 0.7) return "#ef4444"; // red-500
  if (intensity > 0.4) return "#f59e0b"; // amber-500
  return "#3b82f6"; // blue-500
};

export default function HeatMap() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-full bg-muted/20 animate-pulse rounded-lg flex items-center justify-center">
        <span className="text-muted-foreground text-sm">Initializing Geolocation Module...</span>
      </div>
    );
  }

  return (
    <div className="w-full h-full rounded-lg overflow-hidden border border-border relative z-0">
      <MapContainer 
        center={[40.7128, -74.0060]} 
        zoom={11} 
        scrollWheelZoom={false}
        className="w-full h-full"
        style={{ background: "#0a0a0a" }} // Matches dark theme
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        {crimeData.map((crime) => (
          <CircleMarker
            key={crime.id}
            center={[crime.lat, crime.lng]}
            radius={crime.intensity * 20}
            pathOptions={{
              fillColor: getIntensityColor(crime.intensity),
              color: getIntensityColor(crime.intensity),
              weight: 1,
              opacity: 0.8,
              fillOpacity: 0.4,
            }}
          >
            <Popup className="bg-card text-card-foreground border-border">
              <div className="p-1">
                <p className="font-bold text-sm mb-1">{crime.type}</p>
                <p className="text-xs text-muted-foreground">Severity: {(crime.intensity * 100).toFixed(0)}%</p>
                <p className="text-xs text-muted-foreground">Lat: {crime.lat}, Lng: {crime.lng}</p>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <div className="absolute top-4 right-4 z-[400] bg-background/80 backdrop-blur-md p-2 rounded border border-border shadow-lg">
        <div className="text-xs font-semibold mb-2">Threat Level</div>
        <div className="flex items-center gap-2 text-xs">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div> Low
        </div>
        <div className="flex items-center gap-2 text-xs">
          <div className="w-3 h-3 rounded-full bg-amber-500"></div> Medium
        </div>
        <div className="flex items-center gap-2 text-xs">
          <div className="w-3 h-3 rounded-full bg-red-500"></div> High
        </div>
      </div>
    </div>
  );
}
