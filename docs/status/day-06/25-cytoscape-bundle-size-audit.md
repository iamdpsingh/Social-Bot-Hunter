# Day 6 Status 25: Frontend Bundle Size & Code Splitting Audit

Bundle analysis:
- Cytoscape is dynamically imported or lazy-loaded on `/investigations/[id]/graph`.
- Main investigation overview route (`/investigations/[id]`) retains fast initial paint.
- Total JavaScript chunk increase kept under acceptable thresholds.
