import { API_CONFIG } from "@/config/api";
import type { HealthResponse, ReadyResponse } from "@/types/api";

async function fetchWithTimeout(
  url: string,
  timeoutMs: number
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: controller.signal, cache: "no-store" });
    return res;
  } finally {
    clearTimeout(timer);
  }
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetchWithTimeout(
    API_CONFIG.proxyHealthPath,
    API_CONFIG.timeoutMs
  );
  if (!res.ok) throw new Error(`/api/proxy/health returned ${res.status}`);
  return res.json() as Promise<HealthResponse>;
}

export async function fetchReady(): Promise<ReadyResponse> {
  const res = await fetchWithTimeout(
    API_CONFIG.proxyReadyPath,
    API_CONFIG.timeoutMs
  );
  if (!res.ok) throw new Error(`/api/proxy/ready returned ${res.status}`);
  return res.json() as Promise<ReadyResponse>;
}
