export interface HealthResponse {
  status: "ok" | string;
  ts_utc: string;
  service: string;
  version: string;
}

export interface ReadyResponse {
  status: "ready" | string;
  ts_utc: string;
  deps: Record<string, string>;
}

export type ApiStatus = "ok" | "degraded" | "unknown";

export interface ApiHealthState {
  health: HealthResponse | null;
  ready: ReadyResponse | null;
  status: ApiStatus;
  loading: boolean;
  error: string | null;
  lastCheckedAt: string | null;
}
