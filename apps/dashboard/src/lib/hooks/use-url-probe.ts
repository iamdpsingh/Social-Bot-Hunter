"use client";

import { useState, useCallback } from "react";
import { endpoints } from "../api/endpoints";
import { ProbeAccountResponse, ValidateUrlResponse } from "../api/types";

export type ProbeState = "idle" | "validating" | "probing" | "ready" | "error";

export function useUrlProbe() {
  const [state, setState] = useState<ProbeState>("idle");
  const [urlInfo, setUrlInfo] = useState<ValidateUrlResponse | null>(null);
  const [probeResult, setProbeResult] = useState<ProbeAccountResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const reset = useCallback(() => {
    setState("idle");
    setUrlInfo(null);
    setProbeResult(null);
    setErrorMessage(null);
  }, []);

  const probe = useCallback(async (rawUrl: string, platformHint?: string) => {
    setState("validating");
    setErrorMessage(null);

    try {
      // 1. Validate URL
      const valRes = await fetch(endpoints.validateUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: rawUrl, platform_hint: platformHint }),
      });

      if (!valRes.ok) {
        const err = await valRes.json();
        throw new Error(err.detail || "URL validation failed");
      }

      const valData: ValidateUrlResponse = await valRes.json();
      setUrlInfo(valData);
      setState("probing");

      // 2. Conduct preflight probe
      const probeRes = await fetch(endpoints.probeAccount(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: valData.canonical_url, platform_hint: valData.platform }),
      });

      if (!probeRes.ok) {
        const err = await probeRes.json();
        throw new Error(err.detail || "Profile probe failed");
      }

      const probeData: ProbeAccountResponse = await probeRes.json();
      setProbeResult(probeData);
      setState("ready");
      return probeData;
    } catch (e: any) {
      setErrorMessage(e.message || "An unexpected error occurred during profile probe");
      setState("error");
      return null;
    }
  }, []);

  return {
    state,
    urlInfo,
    probeResult,
    errorMessage,
    probe,
    reset,
  };
}
