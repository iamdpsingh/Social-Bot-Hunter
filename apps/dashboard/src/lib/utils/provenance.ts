export function isSyntheticObservation(data: Record<string, unknown>): boolean {
  if (data.is_synthetic === true || data.synthetic === true) return true;
  if (typeof data.account_id === "string" && data.account_id.startsWith("synth_")) return true;
  if (typeof data.scan_id === "string" && data.scan_id.startsWith("synth_")) return true;
  return false;
}
