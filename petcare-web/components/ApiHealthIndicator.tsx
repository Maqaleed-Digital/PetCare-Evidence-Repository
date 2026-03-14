"use client";

import { useApiHealth } from "@/hooks/useApiHealth";
import { DashboardGrid } from "./DashboardGrid";
import { StatusCard } from "./StatusCard";

export function ApiHealthIndicator() {
  const { health, ready, status, loading, error, lastCheckedAt } =
    useApiHealth();

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">
          API Status
        </h2>
        {loading && (
          <span className="text-xs text-gray-400 animate-pulse">
            Checking...
          </span>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
          {error}
        </p>
      )}

      <DashboardGrid>
        <StatusCard
          title="Health"
          value={health?.status ?? (loading ? "…" : "unavailable")}
          status={
            health?.status === "ok"
              ? "ok"
              : health
              ? "degraded"
              : "unknown"
          }
          sub={health?.ts_utc ?? null}
        />
        <StatusCard
          title="Ready"
          value={ready?.status ?? (loading ? "…" : "unavailable")}
          status={
            ready?.status === "ready"
              ? "ok"
              : ready
              ? "degraded"
              : "unknown"
          }
          sub={ready?.ts_utc ?? null}
        />
        <StatusCard
          title="Overall"
          value={
            loading
              ? "…"
              : status === "ok"
              ? "Operational"
              : status === "degraded"
              ? "Degraded"
              : "Unknown"
          }
          status={status}
          sub={lastCheckedAt ?? null}
        />
      </DashboardGrid>
    </section>
  );
}
