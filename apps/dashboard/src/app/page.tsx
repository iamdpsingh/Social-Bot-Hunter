"use client";

import React, { useState } from "react";
import { SystemHealthStrip } from "../components/overview/system-health-strip";
import { MetricsOverviewGrid } from "../components/overview/metrics-overview-grid";
import { RecentScansTable } from "../components/overview/recent-scans-table";
import { PlatformDistributionChart } from "../components/overview/platform-distribution-chart";
import { LiveAuditFeed } from "../components/overview/live-audit-feed";
import { SyntheticDataBanner } from "../components/ui/synthetic-banner";
import { LaunchScanModal } from "../components/overview/launch-scan-modal";

export default function OverviewPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="space-y-6 pb-12">
      {/* Synthetic Provenance Disclosure */}
      <SyntheticDataBanner />

      {/* High-level system health and database connectivity */}
      <SystemHealthStrip />

      {/* Aggregate metrics grid */}
      <MetricsOverviewGrid />

      {/* Core split layout: recent investigations vs platform status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <RecentScansTable onNewScan={() => setIsModalOpen(true)} />
        </div>
        <div className="space-y-6">
          <PlatformDistributionChart />
          <LiveAuditFeed />
        </div>
      </div>

      <LaunchScanModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}
