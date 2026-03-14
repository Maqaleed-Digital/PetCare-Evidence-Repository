# Shared API Conventions — petcare platform

## Version

`petcare-api-conventions-v1` · Phase PH-FND-3

## Base URL

All internal service endpoints are rooted at:

```
http://{service-name}.svc.cluster.local/v1/{service-prefix}/
```

External-facing proxy paths (if any) are routed through the API gateway and are not
covered by these internal conventions.

## Protocol

- HTTP/1.1 inside the cluster.
- TLS 1.2+ enforced at the ingress boundary; internal traffic is mTLS via service mesh.
- All request and response bodies are `application/json; charset=utf-8`.

## HTTP Methods

| Method | Semantics                                 |
|--------|-------------------------------------------|
| GET    | Read. Idempotent. No body.                |
| POST   | Create or trigger an action.              |
| PATCH  | Partial update (JSON Merge Patch, RFC 7396). |
| DELETE | Delete or revoke a resource.              |
| PUT    | Full replace (used rarely — prefer PATCH).|

## Authentication

Every request must include a service-issued JWT in the `Authorization` header:

```
Authorization: Bearer <jwt>
```

JWTs are issued by `identity_rbac`. Callers without a valid JWT receive `401 Unauthorized`.

## Request ID

Every request must include (or will have injected by the gateway):

```
X-Request-ID: <uuid-v4>
```

The same value is echoed in every response as `X-Request-ID`. Log correlation uses this
header throughout the platform.

## Timestamps

All timestamps are ISO 8601 / RFC 3339 in UTC with second precision:

```
2026-03-15T10:42:00Z
```

Clients must not send timestamps without a timezone designator.

## Naming Conventions

| Element        | Convention          | Example                      |
|----------------|---------------------|------------------------------|
| JSON keys      | `snake_case`        | `owner_id`, `created_at`     |
| Path segments  | `kebab-case`        | `/v1/signoff/submit-for-review` |
| Enum values    | `snake_case`        | `p1_critical`, `in_transit`  |
| Boolean fields | Positive framing    | `is_active`, `consent_given` |

## Versioning

The API version is embedded in the path (`/v1/`). Breaking changes increment the major
version. Non-breaking additions (new optional fields, new enum values) do not require a
version bump — consumers must be tolerant of unknown fields (Postel's Law).

## Idempotency

POST endpoints that create resources accept an optional:

```
Idempotency-Key: <uuid-v4>
```

If a request with a given key has been processed within the last 24 hours, the original
response is returned without reprocessing.

## Rate Limiting

Service-to-service calls are not rate-limited by default. External-facing endpoints (if
exposed) are subject to gateway-level rate limiting. Rate-limited responses return `429`
with a `Retry-After` header.

## Health Endpoints

Every service exposes:

```
GET /v1/{prefix}/health
→ 200 { "status": "ok", "service": "...", "version": "..." }
```

No authentication required on health endpoints.
