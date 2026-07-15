"use client";

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { name: "00:00", active: 400, predicted: 420 },
  { name: "04:00", active: 300, predicted: 310 },
  { name: "08:00", active: 550, predicted: 500 },
  { name: "12:00", active: 800, predicted: 850 },
  { name: "16:00", active: 1100, predicted: 1050 },
  { name: "20:00", active: 950, predicted: 1000 },
  { name: "23:59", active: 600, predicted: 650 },
];

export default function CrimeTrendChart() {
  return (
    <div className="w-full h-[300px] mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <defs>
            <linearGradient id="colorActive" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
          <XAxis 
            dataKey="name" 
            stroke="#888888" 
            fontSize={12} 
            tickLine={false}
            axisLine={false}
            dy={10}
          />
          <YAxis 
            stroke="#888888" 
            fontSize={12} 
            tickLine={false}
            axisLine={false}
            dx={-10}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0a0a0a', borderColor: '#333', borderRadius: '8px' }}
            itemStyle={{ color: '#fff' }}
          />
          <Area
            type="monotone"
            dataKey="active"
            stroke="#3b82f6"
            fillOpacity={1}
            fill="url(#colorActive)"
            strokeWidth={2}
            name="Active Incidents"
          />
          <Area
            type="monotone"
            dataKey="predicted"
            stroke="#ef4444"
            fillOpacity={1}
            fill="url(#colorPredicted)"
            strokeWidth={2}
            strokeDasharray="5 5"
            name="AI Predicted"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
