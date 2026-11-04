# Runbook 0028: Synthetic Data Provenance Enforcement

## Objective
Ensure all simulated and imported demo data displays required disclosure banners.

## Policy
Never render scores from `data_origin === 'synthetic'` without the `SyntheticDataBanner`.
