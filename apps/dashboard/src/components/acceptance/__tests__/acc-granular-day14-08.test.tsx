import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { ReadinessScorecard } from '../readiness-scorecard';

describe('AccGranularDay1408', () => {
  it('renders with zero criteria gracefully', () => {
    render(
      <ReadinessScorecard
        scorecard={{
          compliancePercentage: 0,
          totalCriteria: 0,
          verifiedCriteria: 0,
          overallStatus: 'DEGRADED',
          evaluatedAt: '2026-11-14',
          criteria: [],
        }}
      />
    );
    expect(screen.getByText('0%')).toBeInTheDocument();
  });
});
