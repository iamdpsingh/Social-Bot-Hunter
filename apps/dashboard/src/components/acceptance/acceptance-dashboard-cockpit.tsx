import React from 'react';
import { BenchmarkSlaEntry, LaunchChecklistItem, SystemReadinessScorecard } from '../../lib/types/acceptance';
import { E2EPipelineStepper } from './e2e-pipeline-stepper';
import { LaunchChecklistCard } from './launch-checklist-card';
import { LatencyBenchmarkTable } from './latency-benchmark-table';
import { ReadinessScorecard } from './readiness-scorecard';

interface Props {
  scorecard: SystemReadinessScorecard;
  checklist: LaunchChecklistItem[];
  benchmarks: BenchmarkSlaEntry[];
}

export function AcceptanceDashboardCockpit({ scorecard, checklist, benchmarks }: Props) {
  return (
    <div className="space-y-6">
      <ReadinessScorecard scorecard={scorecard} />
      <E2EPipelineStepper />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LaunchChecklistCard items={checklist} />
        <LatencyBenchmarkTable entries={benchmarks} />
      </div>
    </div>
  );
}
