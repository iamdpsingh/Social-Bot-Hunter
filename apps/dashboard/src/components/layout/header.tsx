"use client";

import React from "react";
import { Activity, Shield, Plus, Database } from "lucide-react";
import { Button } from "../ui/button";
import { useHealth } from "../../lib/hooks/use-health";

export interface HeaderProps {
  onNewScanClick?: () => void;
}

export function Header({ onNewScanClick }: HeaderProps) {
  const { health, isLoading } = useHealth();

  return (
    <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-white/5 bg-background/80 px-6 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary border border-primary/20">
          <Shield className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-foreground flex items-center gap-2">
            Social Bot Hunter
            <span className="rounded bg-primary/20 px-1.5 py-0.2 text-[10px] font-mono text-primary font-normal">
              v0.1.0
            </span>
          </h1>
          <p className="text-[11px] text-muted-foreground hidden sm:block">
            Evidence-Driven Account & Coordinated Network Detection
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* System Health Status Indicator */}
        <div className="flex items-center gap-2 rounded-full border border-white/5 bg-white/5 px-3 py-1 text-xs">
          <span
            className={`h-2 w-2 rounded-full ${
              isLoading
                ? "bg-slate-400 animate-pulse"
                : health?.status === "ok"
                ? "bg-emerald-400"
                : "bg-red-400"
            }`}
          />
          <span className="text-[11px] font-medium text-muted-foreground flex items-center gap-1.5">
            <Database className="h-3 w-3" />
            {isLoading ? "Checking..." : health?.database === "connected" ? "Postgres/SQLite Live" : "Offline"}
          </span>
        </div>

        {onNewScanClick && (
          <Button size="sm" onClick={onNewScanClick} className="gap-1.5 shadow-sm">
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">New Investigation</span>
          </Button>
        )}
      </div>
    </header>
  );
}
