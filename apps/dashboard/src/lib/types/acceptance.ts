export interface AcceptanceCriterion {
  id: string;
  section: string;
  title: string;
  description: string;
  verified: boolean;
  testSuite: string;
}

export interface SystemReadinessScorecard {
  compliancePercentage: number;
  totalCriteria: number;
  verifiedCriteria: number;
  overallStatus: 'PRODUCTION_READY' | 'DEGRADED' | 'UNREADY';
  evaluatedAt: string;
  criteria: AcceptanceCriterion[];
}

export interface LaunchChecklistItem {
  dayNumber: number;
  title: string;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'PENDING';
  commitsCount: number;
  signoffDate: string;
}

export interface BenchmarkSlaEntry {
  taskName: string;
  p50Ms: number;
  p90Ms: number;
  p99Ms: number;
  slaLimitMs: number;
  passedSla: boolean;
  throughputOpsSec: number;
}
