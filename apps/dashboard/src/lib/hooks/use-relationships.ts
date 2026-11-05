"use client";

import useSWR from "swr";
import { apiClient } from "../api/client";
import { ENDPOINTS } from "../api/endpoints";
import type { RelationshipListResponse } from "../api/types";

export function useRelationships(
  scanId: string | null,
  options?: { relationshipType?: string; limit?: number; offset?: number }
) {
  const queryParams = new URLSearchParams();
  if (options?.limit) queryParams.set("limit", String(options.limit));
  if (options?.offset) queryParams.set("offset", String(options.offset));
  if (options?.relationshipType) queryParams.set("relationship_type", options.relationshipType);

  const qs = queryParams.toString();
  const url = scanId ? `${ENDPOINTS.scans.relationships(scanId)}${qs ? `?${qs}` : ""}` : null;

  const { data, error, isLoading, mutate } = useSWR<RelationshipListResponse>(url, apiClient, {
    revalidateOnFocus: false,
  });

  return {
    relationships: data?.relationships || [],
    total: data?.total || 0,
    offset: data?.offset || 0,
    limit: data?.limit || options?.limit || 50,
    isLoading,
    isError: !!error,
    error,
    mutate,
  };
}
