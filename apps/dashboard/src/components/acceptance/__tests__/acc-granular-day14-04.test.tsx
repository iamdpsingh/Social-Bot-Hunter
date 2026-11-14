import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { E2EPipelineStepper } from '../e2e-pipeline-stepper';

describe('AccGranularDay1404', () => {
  it('renders detail text for detection stage', () => {
    render(<E2EPipelineStepper />);
    expect(screen.getByText('Heuristic + ML scoring')).toBeInTheDocument();
  });
});
