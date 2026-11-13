import {
  DependencyAuditResponse,
  PrivacyScanResponse,
  SecretScanResponse,
  SecurityScorecardResponse,
} from '../types/security';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchSecurityScorecard(): Promise<SecurityScorecardResponse> {
  const res = await fetch(`${API_BASE}/security/scorecard`);
  if (!res.ok) {
    throw new Error(`Failed to fetch security scorecard: ${res.statusText}`);
  }
  return res.json();
}

export async function triggerSecretScan(): Promise<SecretScanResponse> {
  const res = await fetch(`${API_BASE}/security/scan-secrets`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to trigger secret scan: ${res.statusText}`);
  }
  return res.json();
}

export async function triggerPrivacyScan(): Promise<PrivacyScanResponse> {
  const res = await fetch(`${API_BASE}/security/scan-privacy`, {
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error(`Failed to trigger privacy scan: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchDependencyVulnerabilities(): Promise<DependencyAuditResponse> {
  const res = await fetch(`${API_BASE}/security/dependencies`);
  if (!res.ok) {
    throw new Error(`Failed to fetch dependency vulnerabilities: ${res.statusText}`);
  }
  return res.json();
}
