"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchHealth, fetchReady } from "@/services/api.service";
import type { ApiHealthState } from "@/types/api";

const POLL_INTERVAL_MS = 30_000;

const initialState: ApiHealthState = {
  health: null,
  ready: null,
  status: "unknown",
  loading: true,
  error: null,
  lastCheckedAt: null,
};

export function useApiHealth(): ApiHealthState {
  const [state, setState] = useState<ApiHealthState>(initialState);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const check = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const [health, ready] = await Promise.all([fetchHealth(), fetchReady()]);
      const allOk =
        health.status === "ok" && ready.status === "ready";
      setState({
        health,
        ready,
        status: allOk ? "ok" : "degraded",
        loading: false,
        error: null,
        lastCheckedAt: new Date().toISOString(),
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown error";
      setState((prev) => ({
        ...prev,
        status: "degraded",
        loading: false,
        error: message,
        lastCheckedAt: new Date().toISOString(),
      }));
    }
  }, []);

  useEffect(() => {
    check();
    intervalRef.current = setInterval(check, POLL_INTERVAL_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [check]);

  return state;
}
