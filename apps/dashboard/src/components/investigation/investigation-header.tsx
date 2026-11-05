import React from "react";
import { ArrowLeft, Clock } from "lucide-react";
import Link from "next/link";
import { ScanStatusBadge } from "../ui/badge";
import { PlatformIcon } from "../ui/platform-icon";
import { SyntheticDataBanner } from "../ui/synthetic-banner";
import type { ScanJob } from "../../lib/api/types";

export interface InvestigationHeaderProps {
  scan?: ScanJob;
  scanId?: string;
  target?: string;
  platform?: any;
  status?: string;
  totalAccounts?: number;
  botAccounts?: number;
  onExportClick?: () => void;
}

export function InvestigationHeader({
  scan,
  scanId: propScanId,
  target: propTarget,
  platform: propPlatform = "x",
  status: propStatus = "completed",
  totalAccounts,
  botAccounts,
  onExportClick,
}: InvestigationHeaderProps) {
  const scanId = scan?.id || propScanId || "unknown";
  const target = scan?.requested_by || propTarget || scanId;
  const platform = scan?.platform || propPlatform;
  const status = scan?.status || propStatus;
  const isSynthetic = scan?.data_origin === "synthetic";

  return (
    <div className="space-y-4" data-testid="investigation-header">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Link href="/" className="hover:text-foreground flex items-center gap-1 transition-colors">
          <ArrowLeft className="h-3 w-3" /> Back to Overview
        </Link>
        <span>/</span>
        <span className="font-mono text-foreground">{scanId}</span>
      </div>

      {isSynthetic && <SyntheticDataBanner />}

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/5 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <PlatformIcon platform={platform} size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
              Investigation: {target}
              <ScanStatusBadge status={status as any} />
            </h1>
            <p className="text-xs text-muted-foreground flex items-center gap-2">
              <Clock className="h-3 w-3" />
              <span>Created {scan?.created_at ? new Date(scan.created_at).toLocaleString() : new Date().toLocaleDateString()}</span>
              {totalAccounts !== undefined && (
                <>
                  <span>•</span>
                  <span>{totalAccounts} Accounts Analyzed</span>
                </>
              )}
            </p>
          </div>
        </div>

        {onExportClick && (
          <button
            type="button"
            onClick={onExportClick}
            className="px-3 py-1.5 text-xs font-medium rounded-md border border-border bg-card hover:bg-muted/30 transition-colors"
          >
            Export Data
          </button>
        )}
      </div>
    </div>
  );
}
