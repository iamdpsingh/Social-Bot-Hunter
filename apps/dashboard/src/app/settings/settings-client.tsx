"use client";

import React from "react";
import { usePlatformQuotas, useRetentionSettings } from "../../lib/hooks/use-settings";
import { PlatformCapabilityCard } from "../../components/settings/platform-capability-card";
import { RetentionConfigCard } from "../../components/settings/retention-config-card";

export function SettingsClient() {
  const { stats, mutate: mutateRetention } = useRetentionSettings(90);
  const { quotas } = usePlatformQuotas();

  const handlePurge = async (days: number, dryRun: boolean) => {
    const res = await fetch("/api/v1/settings/retention/purge", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ retention_days: days, dry_run: dryRun }),
    });
    if (!res.ok) throw new Error("Purge failed");
    await mutateRetention();
  };

  return (
    <div data-testid="settings-page" className="space-y-8">
      <div>
        <h2 className="text-2xl font-black text-foreground">Platform Settings & Governance</h2>
        <p className="text-xs text-muted-foreground mt-1">
          Manage API quotas, social media platform capabilities, and data retention privacy policies.
        </p>
      </div>

      <PlatformCapabilityCard quotas={quotas} />

      <RetentionConfigCard stats={stats} onPurge={handlePurge} />
    </div>
  );
}
