# Runbook 0048: Investigating Reciprocal Follow Rings (Sybil Swarms)

## Characteristics
- Suspicious accounts with near 100% mutual following reciprocity.
- High internal edge density (cluster cohesion > 0.8).
- Minimal edges connected to organic accounts outside the cluster.

## Procedure
1. Check **Graph Metrics Card** reciprocity percentage (> 40% is suspicious).
2. Switch layout to **Circular**.
3. Inspect whether accounts form a closed perimeter ring.
4. Export cluster JSON bundle for remediation.
