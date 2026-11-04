"use client";

import React from "react";
import { Activity, ShieldCheck, UserCheck, AlertOctagon } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { useAudit } from "../../lib/hooks/use-audit";
import { Skeleton } from "../ui/skeleton";

export function LiveAuditFeed() {
  const { events, isLoading } = useAudit(8);

  const getActionBadge = (action: string) => {
    if (action.includes("create")) {
      return { color: "text-blue-400 bg-blue-500/10 border-blue-500/20", icon: Activity };
    }
    if (action.includes("cancel") || action.includes("delete")) {
      return { color: "text-amber-400 bg-amber-500/10 border-amber-500/20", icon: AlertOctagon };
    }
    if (action.includes("auth") || action.includes("user")) {
      return { color: "text-purple-400 bg-purple-500/10 border-purple-500/20", icon: UserCheck };
    }
    return { color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20", icon: ShieldCheck };
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Audit Trail</CardTitle>
        <CardDescription>Immutable record of pipeline lifecycle transitions and user actions</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          [...Array(4)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)
        ) : events.length === 0 ? (
          <p className="text-xs text-muted-foreground text-center py-4">No audit events recorded yet.</p>
        ) : (
          events.map((evt) => {
            const { color, icon: Icon } = getActionBadge(evt.action);
            return (
              <div
                key={evt.id}
                className="flex items-center justify-between text-xs p-2 rounded-lg bg-white/5 border border-white/5"
              >
                <div className="flex items-center gap-2.5">
                  <div className={`p-1.5 rounded-md border ${color}`}>
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <span className="font-mono font-medium text-foreground">{evt.action}</span>
                    <p className="text-[10px] text-muted-foreground">
                      Actor: <span className="font-mono">{evt.actor}</span>
                    </p>
                  </div>
                </div>
                <span className="font-mono text-[10px] text-muted-foreground">
                  {new Date(evt.occurred_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
}
