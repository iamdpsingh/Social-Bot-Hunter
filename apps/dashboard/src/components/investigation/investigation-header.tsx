import React from "react";
import { ArrowLeft, Clock } from "lucide-react";
import Link from "next/link";
import { ScanStatusBadge } from "../ui/badge";
import { PlatformIcon } from "../ui/platform-icon";
import { SyntheticDataBanner } from "../ui/synthetic-banner";
import type { ScanJob } from "../../lib/api/types";

export interface InvestigationHeaderProps {
  scan?: ScanJob;
}

export function InvestigationHeader({ scan }: InvestigationHeaderProps) {
  if (!scan) return null;
  const isSynthetic = scan.data_origin === "synthetic";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Link href="/" className="hover:text-foreground flex items-center gap-1 transition-colors">
          <ArrowLeft className="h-3 w-3" /> Back to Overview
        </Link>
        <span>/</span>
        <span className="font-mono text-foreground">{scan.id}</span>
      </div>

      {isSynthetic && <SyntheticDataBanner />}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <PlatformIcon platform={scan.platform} size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
              Investigation: {scan.requested_by}
              <ScanStatusBadge status={scan.status} />
            </h1>
            <p className="text-xs text-muted-foreground flex items-center gap-2">
              <Clock className="h-3 w-3" />
              <span>Created {new Date(scan.created_at).toLocaleString()}</span>
              <span>•</span>
              <span className="uppercase font-mono">{scan.collection_mode}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
