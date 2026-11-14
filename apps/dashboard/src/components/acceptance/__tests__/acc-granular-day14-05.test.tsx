import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { E2EPipelineStepper } from '../e2e-pipeline-stepper';

describe('AccGranularDay1405', () => {
  it('renders custom step', () => {
    render(
      <E2EPipelineStepper
        steps={[
          {
            id: 'custom-1',
            name: 'Custom Verification',
            detail: 'Running smoke check',
            status: 'COMPLETED',
          },
        ]}
      />
    );
    expect(screen.getByText('CUSTOM VERIFICATION')).toBeInTheDocument();
    expect(screen.getByText('Running smoke check')).toBeInTheDocument();
  });
});
