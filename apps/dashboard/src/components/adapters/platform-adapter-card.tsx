"use client";

import React from "react";
import { Youtube, Twitter, Instagram, Video, Building2, ShieldCheck, Zap } from "lucide-react";
import { PlatformQuotaStatus } from "../../lib/api/types";
import { Badge } from "../ui/badge";
import { QuotaMeter } from "./quota-meter";
import { cn } from "../../lib/utils";

interface PlatformAdapterCardProps {
  quota: PlatformQuotaStatus;
  className?: string;
}

export function PlatformAdapterCard({ quota, className }: PlatformAdapterCardProps) {
  const plat = quota.platform.toLowerCase();
  
  let Icon = Youtube;
  let iconColor = "text-red-500";
  let subtitle = "Data API v3 Official Adapter";

  if (plat === "x" || plat === "twitter") {
    Icon = Twitter;
    iconColor = "text-sky-400";
    subtitle = "X API v2 Official Adapter";
  } else if (plat === "instagram") {
    Icon = Instagram;
    iconColor = "text-pink-500";
    subtitle = "Graph API v21.0 Business Discovery";
  } else if (plat === "tiktok") {
    Icon = Video;
    iconColor = "text-cyan-400";
    subtitle = "Research & Display API v2";
  } else if (plat === "linkedin") {
    Icon = Building2;
    iconColor = "text-blue-500";
    subtitle = "Community Management API v2 (Official)";
  }

  return (
    <div
      className={cn(
        "rounded-xl border border-white/10 bg-card/60 p-5 shadow-lg backdrop-blur-md space-y-4 hover:border-white/20 transition-all",
        className
      )}
      data-testid={`adapter-card-${quota.platform}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/5 border border-white/10">
            <Icon className={cn("h-5 w-5", iconColor)} />
          </div>
          <div>
            <h3 className="font-semibold text-sm capitalize text-foreground">{quota.platform} Data API</h3>
            <p className="text-xs text-muted-foreground">{subtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant={quota.status === "active" ? "success" : "warning"} className="capitalize">
            {quota.status}
          </Badge>
        </div>
      </div>

      <QuotaMeter
        platform={quota.platform}
        dailyLimit={quota.daily_quota_limit}
        unitsUsed={quota.quota_used_today}
      />

      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5 text-xs">
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span className="truncate">{quota.auth_state.replace(/_/g, " ")}</span>
        </div>
        <div className="flex items-center justify-end gap-1.5 text-muted-foreground">
          <Zap className="h-3.5 w-3.5 text-amber-400" />
          <span>{quota.rate_limit_rpm} req/min limit</span>
        </div>
      </div>
    </div>
  );
}
