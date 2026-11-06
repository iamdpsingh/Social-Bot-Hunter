import { describe, expect, it } from "vitest";
import { ENDPOINTS } from "../endpoints";

describe("networks graph endpoints", () => {
  it("generates correct paths for network subrouter", () => {
    expect(ENDPOINTS.networks.clusters("scan_99")).toContain("/scans/scan_99/networks/clusters");
    expect(ENDPOINTS.networks.graph("scan_99")).toContain("/scans/scan_99/networks/graph");
    expect(ENDPOINTS.networks.neighbors("scan_99", "node_1")).toContain("/scans/scan_99/networks/nodes/node_1/neighbors");
    expect(ENDPOINTS.networks.metrics("scan_99")).toContain("/scans/scan_99/networks/metrics");
    expect(ENDPOINTS.networks.export("scan_99")).toContain("/scans/scan_99/networks/export");
  });
});
