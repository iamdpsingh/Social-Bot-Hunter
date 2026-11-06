# Runbook 0049: Managing Large Graph Scale Safeguards (>5,000 Nodes)

## Threshold Rules
- `N < 1,000`: Full animated force-directed layout active.
- `1,000 <= N <= 5,000`: Static force-directed layout without continuous simulation.
- `N > 5,000`: Automatic **GraphScaleAlert** recommendation to Accessible Table view.

## Operational Command
To extract a bounded 500-node high-risk subgraph:
```bash
curl -H "Authorization: Bearer $TOKEN"   "http://localhost:8080/api/v1/scans/{scan_id}/networks/graph?max_nodes=500&min_score=0.75"
```
