"use client";

import React from "react";
import { Bell, ShieldAlert, User, Search, Settings } from "lucide-react";
import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="h-16 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-50 flex items-center justify-between px-6 sticky top-0">
      <div className="flex items-center gap-4">
        <Link href="/" className="flex items-center gap-2">
          <ShieldAlert className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold tracking-tighter text-foreground">
            Sentinel AI
          </span>
        </Link>
        <div className="hidden md:flex ml-8 relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <input
            type="search"
            placeholder="Search intelligence database..."
            className="h-9 w-64 md:w-80 lg:w-96 rounded-md border border-input bg-transparent pl-9 pr-4 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <button className="relative p-2 text-muted-foreground hover:text-foreground transition-colors">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive"></span>
        </button>
        <button className="p-2 text-muted-foreground hover:text-foreground transition-colors">
          <Settings className="h-5 w-5" />
        </button>
        <div className="h-8 w-8 rounded-full bg-primary/20 border border-primary/50 flex items-center justify-center">
          <User className="h-4 w-4 text-primary" />
        </div>
      </div>
    </nav>
  );
}
