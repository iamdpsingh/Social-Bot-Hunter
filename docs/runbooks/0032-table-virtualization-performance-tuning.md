# Runbook 0032: Table Virtualization Performance Tuning

## Objective
Tune table virtualization row heights and overscan buffers when experiencing frame drops during scroll.

## Tuning Actions
1. Open `apps/dashboard/src/tokens/table-virtualization.ts`.
2. Adjust `rowHeight` to match rendered row styles (`52px` default).
3. Increase `overscan` from `5` to `8` if fast scrolling causes white space flashes.
