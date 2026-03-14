# API Integration — petcare-web (PH-UI-1A)

## Canonical Upstream

```
https://api.myveticare.com
```

## Problem: Browser CORS

The browser cannot call `https://api.myveticare.com` directly without the
upstream setting permissive CORS headers. Modifying the upstream is out of
scope for PH-UI-1A (infra activation only). The solution is a server-side proxy.

## Solution: Next.js Route Handlers as Proxy

Two Route Handlers run server-side (Node.js, not the browser):

| Proxy route              | Upstream target                        |
|--------------------------|----------------------------------------|
| `GET /api/proxy/health`  | `https://api.myveticare.com/health`    |
| `GET /api/proxy/ready`   | `https://api.myveticare.com/ready`     |

The browser calls only same-origin paths (`/api/proxy/*`). The Next.js server
calls the upstream with a `User-Agent: petcare-web-proxy/1.0` header and
forwards the response body and status code verbatim.

## Contract Validation

The `useApiHealth` hook checks:

- `/health` response: `status === "ok"` and `ts_utc` present
- `/ready` response: `status === "ready"`, `deps` is an object, `ts_utc` present

Deviations set `ApiHealthState.status` to `"degraded"`.

## Poll Interval

30 seconds (configurable via `POLL_INTERVAL_MS` in `hooks/useApiHealth.ts`).

## Timeout

8 000 ms per request (configurable in `config/api.ts` → `timeoutMs`).

## Error Handling

- Network / timeout errors: `status → "degraded"`, `error` field populated.
- Upstream non-200: proxy returns the upstream status; hook sets `"degraded"`.
- Upstream 502 from proxy: upstream unreachable.

## No Secrets

No API keys or tokens are required for the health/ready endpoints. The proxy
adds only a `User-Agent` header for observability.
