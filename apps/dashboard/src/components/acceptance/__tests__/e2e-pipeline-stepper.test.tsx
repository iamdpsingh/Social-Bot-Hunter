import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, expect, it } from 'vitest';
import { E2EPipelineStepper } from '../e2e-pipeline-stepper';

describe('E2EPipelineStepper', () => {
  it('renders all default pipeline stages', () => {
    render(<E2EPipelineStepper />);
    expect(screen.getByText('End-to-End Pipeline Verification')).toBeInTheDocument();
    expect(screen.getByText('INGESTION')).toBeInTheDocument();
    expect(screen.getByText('NETWORK GRAPH')).toBeInTheDocument();
  });
});
