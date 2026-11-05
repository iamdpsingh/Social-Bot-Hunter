import type { AccountAssessment } from "../api/types";

export function filterAccounts(
  accounts: AccountAssessment[],
  query?: string,
  bandFilter?: string
): AccountAssessment[] {
  let filtered = accounts;

  if (bandFilter && bandFilter !== "all") {
    filtered = filtered.filter((acc) => acc.band === bandFilter);
  }

  if (query && query.trim() !== "") {
    const q = query.toLowerCase().trim();
    filtered = filtered.filter((acc) => {
      const usernameMatch = acc.username ? acc.username.toLowerCase().includes(q) : false;
      const idMatch = acc.platform_account_id.toLowerCase().includes(q);
      const pidMatch = acc.pid.toLowerCase().includes(q);
      return usernameMatch || idMatch || pidMatch;
    });
  }

  return filtered;
}
