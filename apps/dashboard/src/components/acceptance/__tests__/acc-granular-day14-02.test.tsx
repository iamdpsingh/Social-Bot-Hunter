import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { ReadinessScorecard } from '../readiness-scorecard';

describe('AccGranularDay1402', () => {
  it('renders DEGRADED status badge', () => {
    render(
      <ReadinessScorecard
        scorecard={{
          compliancePercentage: 80,
          totalCriteria: 5,
          verifiedCriteria: 4,
          overallStatus: 'DEGRADED',
          evaluatedAt: '2026-11-14',
          criteria: [],
        }}
      />
    );
    expect(screen.getByText('DEGRADED')).toBeInTheDocument();
  });
});
