# Day 6 Status 02: Backend Graph APIs Delivery

Delivered graph subgraph query endpoints:
- `GET /api/v1/scans/{scan_id}/networks/graph` with filtering by risk band, min score, and max nodes.
- `GET /api/v1/scans/{scan_id}/networks/nodes/{node_id}/neighbors` for ego-network exploration.
- `GET /api/v1/scans/{scan_id}/networks/metrics` for macro graph topology metrics.
- `GET /api/v1/scans/{scan_id}/networks/export` for Cytoscape JSON bundles.
