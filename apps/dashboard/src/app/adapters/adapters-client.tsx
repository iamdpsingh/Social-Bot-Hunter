"use client";

import React, { useState } from "react";
import { Radio, Search, RefreshCw } from "lucide-react";
import { Button } from "../../components/ui/button";
import { PlatformAdapterCard } from "../../components/adapters/platform-adapter-card";
import { AdapterTelemetryTable } from "../../components/adapters/adapter-telemetry-table";
import { UrlProbeModal } from "../../components/adapters/url-probe-modal";
import { useAdapterQuotas } from "../../lib/hooks/use-adapter-quotas";
import { useAdapterTelemetry } from "../../lib/hooks/use-adapter-telemetry";

export function AdaptersClient() {
  const [isProbeOpen, setIsProbeOpen] = useState(false);
  const { quotas, isLoading: quotasLoading, mutate: refreshQuotas } = useAdapterQuotas();
  const { telemetry, isLoading: telemetryLoading, mutate: refreshTelemetry } = useAdapterTelemetry();

  const handleRefreshAll = () => {
    refreshQuotas();
    refreshTelemetry();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-white/5 pb-5">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Radio className="h-5 w-5 text-primary" />
            Platform Adapters & Quota Management
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Monitor official third-party social API integrations, rate limit windows, and daily quotas.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleRefreshAll} disabled={quotasLoading}>
            <RefreshCw className={`mr-1.5 h-3.5 w-3.5 ${quotasLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setIsProbeOpen(true)}>
            <Search className="mr-1.5 h-3.5 w-3.5" />
            Probe Profile URL
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {quotas.map((q) => (
          <PlatformAdapterCard key={q.platform} quota={q} />
        ))}
      </div>

      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-foreground">Live Adapter Telemetry</h2>
        <AdapterTelemetryTable telemetry={telemetry} />
      </div>

      <UrlProbeModal isOpen={isProbeOpen} onClose={() => setIsProbeOpen(false)} />
    </div>
  );
}
