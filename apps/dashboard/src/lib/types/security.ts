export interface SecretFindingItem {
  rule_id: string;
  rule_name: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  file_path: string;
  line_number: number;
  masked_value: string;
  entropy: number;
}

export interface SecretScanResponse {
  target_dir: string;
  total_findings: number;
  findings: SecretFindingItem[];
  passed: boolean;
}

export interface PIIFindingItem {
  pii_type: 'EMAIL' | 'PHONE' | 'IPV4' | 'GPS' | 'CREDIT_CARD';
  masked_value: string;
  location: string;
  line_number: number;
}

export interface PrivacyScanResponse {
  passed: boolean;
  total_findings: number;
  scanned_sources: number;
  findings: PIIFindingItem[];
}

export interface DependencyFindingItem {
  package_name: string;
  installed_version: string;
  ecosystem: string;
  advisory_id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  patched_version: string;
  summary: string;
}

export interface DependencyEcosystemReport {
  ecosystem: string;
  scanned_packages_count: number;
  passed: boolean;
  findings: DependencyFindingItem[];
}

export interface DependencyAuditResponse {
  passed: boolean;
  python: DependencyEcosystemReport;
  node: DependencyEcosystemReport;
}

export interface SecurityCheckItem {
  category: string;
  check_id: string;
  name: string;
  passed: boolean;
  findings_count: number;
  details: Record<string, unknown>;
}

export interface SecurityScorecardResponse {
  passed_audit: boolean;
  total_checks: number;
  passed_checks: number;
  failed_checks: number;
  findings: SecretFindingItem[];
  checks: SecurityCheckItem[];
}
