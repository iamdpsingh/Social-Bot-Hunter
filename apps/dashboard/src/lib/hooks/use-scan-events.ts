"use client";

import { useEffect, useState, useRef } from "react";
import { ENDPOINTS } from "../api/endpoints";
import { getAuthToken } from "../api/client";

export interface LiveScanEvent {
  event_id: string;
  scan_id: string;
  event_type: string;
  stage: string;
  progress_pct: number;
  message: string;
  timestamp: string;
  details: Record<string, unknown>;
}

export function useScanEvents(scanId: string | null) {
  const [events, setEvents] = useState<LiveScanEvent[]>([]);
  const [latestEvent, setLatestEvent] = useState<LiveScanEvent | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isFinished, setIsFinished] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!scanId) {
      setEvents([]);
      setLatestEvent(null);
      setProgress(0);
      setIsConnected(false);
      setIsFinished(false);
      return;
    }

    const token = getAuthToken();
    const url = new URL(ENDPOINTS.scans.events(scanId));
    if (token) {
      url.searchParams.set("token", token);
    }

    const es = new EventSource(url.toString());
    eventSourceRef.current = es;

    es.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    es.onmessage = (e) => {
      try {
        const payload: LiveScanEvent = JSON.parse(e.data);
        setLatestEvent(payload);
        setProgress(payload.progress_pct);
        setEvents((prev) => [...prev.slice(-99), payload]);

        if (
          payload.event_type === "completed" ||
          payload.event_type === "failed" ||
          payload.event_type === "cancelled"
        ) {
          setIsFinished(true);
          es.close();
        }
      } catch (err) {
        console.error("Failed to parse scan event:", err);
      }
    };

    es.onerror = () => {
      setIsConnected(false);
      setError(new Error("EventSource connection lost"));
      es.close();
    };

    return () => {
      es.close();
      setIsConnected(false);
    };
  }, [scanId]);

  return {
    events,
    latestEvent,
    progress,
    isConnected,
    isFinished,
    error,
  };
}
