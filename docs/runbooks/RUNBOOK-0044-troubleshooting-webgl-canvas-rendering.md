# Runbook 0044: Troubleshooting WebGL and Canvas Rendering Issues

## Symptoms
- Canvas appears blank or freezes when loading large scan graph.
- Frame rate drops below 30fps during zoom/pan.

## Remediation Steps
1. Click **Switch to Table View** in the top warning banner.
2. Apply a higher **Min Score** filter (e.g. 70%) to reduce visible node count below 1,000.
3. Click **Reset** in toolbar to recalculate viewport bounding box.
4. If browser hardware acceleration is disabled, enable `chrome://flags/#ignore-gpu-blocklist`.
