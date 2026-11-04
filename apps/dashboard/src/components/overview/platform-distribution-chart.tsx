"use client";

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { PlatformIcon } from "../ui/platform-icon";
import { useCapabilities } from "../../lib/hooks/use-capabilities";
import { useScans } from "../../lib/hooks/use-scans";
import { ProgressBar } from "../ui/progress-bar";
import type { Platform } from "../../lib/api/types";

const PLATFORMS: Array<{ id: Platform; name: string }> = [
  { id: "x", name: "X (Twitter)" },
  { id: "instagram", name: "Instagram" },
  { id: "youtube", name: "YouTube" },
  { id: "tiktok", name: "TikTok" },
  { id: "linkedin", name: "LinkedIn" },
];

export function PlatformDistributionChart() {
  const { capabilities } = useCapabilities();
  const { scans } = useScans(100);

  const getPlatformStats = (platformId: Platform) => {
    const scanCount = scans.filter((s) => s.platform === platformId).length;
    const caps = capabilities.filter((c) => c.platform === platformId);
    const supportedOps = caps.filter((c) => c.supported).length;
    const totalOps = caps.length || 1;
    const coverage = Math.round((supportedOps / totalOps) * 100);

    return { scanCount, coverage };
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Supported Platforms & Scope</CardTitle>
        <CardDescription>Investigation volume and official API capability coverage</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {PLATFORMS.map((platform) => {
          const { scanCount, coverage } = getPlatformStats(platform.id);
          return (
            <div key={platform.id} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 font-medium">
                  <div className="flex h-6 w-6 items-center justify-center rounded bg-white/5 text-foreground">
                    <PlatformIcon platform={platform.id} size={13} />
                  </div>
                  <span>{platform.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-muted-foreground">{scanCount} scans</span>
                  <span className="font-mono text-[10px] text-slate-400 bg-white/5 px-1.5 py-0.5 rounded">
                    {coverage}% supported
                  </span>
                </div>
              </div>
              <ProgressBar
                value={Math.max(coverage, 10)}
                max={100}
                variant={coverage > 60 ? "primary" : coverage > 30 ? "warning" : "destructive"}
              />
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
