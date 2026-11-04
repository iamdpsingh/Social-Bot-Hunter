"use client";

import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";
import { useHealth } from "../../lib/hooks/use-health";
import { Card, CardContent } from "../ui/card";

export function SystemHealthStrip() {
  const { health, isLoading, isError } = useHealth();

  return (
    <Card className="border-white/5 bg-slate-900/40">
      <CardContent className="p-4 flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-muted-foreground uppercase tracking-wider text-[11px]">
              API Status:
            </span>
            {isLoading ? (
              <span className="text-slate-400">Connecting...</span>
            ) : isError ? (
              <span className="flex items-center gap-1.5 text-red-400 font-medium">
                <XCircle className="h-3.5 w-3.5" /> Disconnected
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                <CheckCircle2 className="h-3.5 w-3.5" /> Operational
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 border-l border-white/10 pl-6">
            <span className="font-semibold text-muted-foreground uppercase tracking-wider text-[11px]">
              Database Backend:
            </span>
            <span className="text-slate-300 font-mono text-[11px]">
              {health?.database === "connected" ? "PostgreSQL Pool / SQLite WAL" : "Checking..."}
            </span>
          </div>

          <div className="flex items-center gap-2 border-l border-white/10 pl-6 hidden md:flex">
            <span className="font-semibold text-muted-foreground uppercase tracking-wider text-[11px]">
              Worker Engine:
            </span>
            <span className="text-blue-400 font-medium">Active (Bounded Concurrency)</span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-muted-foreground text-[11px]">
          <Clock className="h-3.5 w-3.5" />
          <span>Last sync: {health?.timestamp ? new Date(health.timestamp).toLocaleTimeString() : "Just now"}</span>
        </div>
      </CardContent>
    </Card>
  );
}
