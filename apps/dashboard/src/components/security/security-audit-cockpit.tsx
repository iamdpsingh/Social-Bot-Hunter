import React from 'react';
import {
  DependencyAuditResponse,
  PrivacyScanResponse,
  SecretScanResponse,
  SecurityScorecardResponse,
} from '../../lib/types/security';
import { SecurityScorecardCard } from './security-scorecard-card';
import { SecretScanCard } from './secret-scan-card';
import { VulnerabilityAdvisoryCard } from './vulnerability-advisory-card';
import { PrivacyAuditCard } from './privacy-audit-card';

interface Props {
  scorecard: SecurityScorecardResponse;
  secrets: SecretScanResponse;
  privacy: PrivacyScanResponse;
  dependencies: DependencyAuditResponse;
  onRefresh?: () => void;
}

export function SecurityAuditCockpit({
  scorecard,
  secrets,
  privacy,
  dependencies,
  onRefresh,
}: Props) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Security & Compliance Audit</h2>
          <p className="text-sm text-muted-foreground">
            Zero-leakage guarantees, offline vulnerability posture, and data protection scorecard.
          </p>
        </div>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition"
          >
            Refresh Scorecard
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SecurityScorecardCard scorecard={scorecard} />
        <SecretScanCard scan={secrets} />
        <VulnerabilityAdvisoryCard audit={dependencies} />
        <PrivacyAuditCard privacy={privacy} />
      </div>
    </div>
  );
}
