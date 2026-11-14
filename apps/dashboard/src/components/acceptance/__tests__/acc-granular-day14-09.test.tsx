import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { ReadinessScorecard } from '../readiness-scorecard';

describe('AccGranularDay1409', () => {
  it('renders unverified item description', () => {
    render(
      <ReadinessScorecard
        scorecard={{
          compliancePercentage: 50,
          totalCriteria: 2,
          verifiedCriteria: 1,
          overallStatus: 'DEGRADED',
          evaluatedAt: '2026-11-14',
          criteria: [
            {
              id: 'UNVER-01',
              section: '19.9',
              title: 'Pending Feature',
              description: 'Experimental module undergoing test',
              verified: false,
              testSuite: 'test.py',
            },
          ],
        }}
      />
    );
    expect(screen.getByText('Pending Feature')).toBeInTheDocument();
  });
});
