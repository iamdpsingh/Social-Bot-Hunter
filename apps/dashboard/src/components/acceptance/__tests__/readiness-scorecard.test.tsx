import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { SystemReadinessScorecard } from '../../../lib/types/acceptance';
import { ReadinessScorecard } from '../readiness-scorecard';

const mockScorecard: SystemReadinessScorecard = {
  compliancePercentage: 100,
  totalCriteria: 2,
  verifiedCriteria: 2,
  overallStatus: 'PRODUCTION_READY',
  evaluatedAt: '2026-11-14T00:00:00Z',
  criteria: [
    {
      id: 'SEC-19.1',
      section: '19.1',
      title: 'Multi-Platform Ingestion',
      description: 'Mock and live adapter ingest for all 5 platforms',
      verified: true,
      testSuite: 'tests/e2e/test_e2e_multi_platform.py',
    },
  ],
};

describe('ReadinessScorecard', () => {
  it('renders overall status and criteria title', () => {
    render(<ReadinessScorecard scorecard={mockScorecard} />);
    expect(screen.getByText('Production Readiness Scorecard')).toBeInTheDocument();
    expect(screen.getByText('PRODUCTION READY')).toBeInTheDocument();
    expect(screen.getByText('Multi-Platform Ingestion')).toBeInTheDocument();
  });
});
