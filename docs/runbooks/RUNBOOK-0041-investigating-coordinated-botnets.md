# Runbook 0041: Investigating Coordinated Botnets via Network Explorer

## Objective
Identify, inspect, and quarantine coordinated botnet swarms using Cytoscape directed canvas.

## Procedure
1. Navigate to `/investigations/{scan_id}/graph`.
2. Inspect the **Cluster Summary Bar** at the top.
3. Click the first cluster pill with highest member count (e.g. `cluster_1`).
4. Switch layout preset to **Concentric by Risk** to isolate high-risk bot hubs in the center.
5. Click the central node to open the **Node Detail Drawer**.
6. Review risk score breakdown and click **View Full Account Profile** to execute quarantine.
