import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { AcceptanceDashboardCockpit } from '../acceptance-dashboard-cockpit';

describe('AcceptanceDashboardCockpit', () => {
  it('renders cockpit subcomponents together', () => {
    render(
      <AcceptanceDashboardCockpit
        scorecard={{
          compliancePercentage: 100,
          totalCriteria: 1,
          verifiedCriteria: 1,
          overallStatus: 'PRODUCTION_READY',
          evaluatedAt: '2026-11-14T00:00:00Z',
          criteria: [],
        }}
        checklist={[]}
        benchmarks={[]}
      />
    );
    expect(screen.getByText('Production Readiness Scorecard')).toBeInTheDocument();
    expect(screen.getByText('14-Day Delivery Checklist')).toBeInTheDocument();
    expect(screen.getByText('Latency Benchmarks & SLAs')).toBeInTheDocument();
  });
});
