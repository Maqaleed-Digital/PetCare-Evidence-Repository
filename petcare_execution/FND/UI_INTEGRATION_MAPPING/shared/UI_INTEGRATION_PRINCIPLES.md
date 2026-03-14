# UI Integration Mapping — Shared Principles

## Version

`petcare-ui-integration-principles-v1` · Phase PH-FND-4

## Purpose

This document defines the governing principles for how petcare-web UI surfaces (PH-UI-1A
through PH-UI-6) will integrate with the backend API contracts defined in PH-FND-3.

All current UI surfaces are **read-only shells with placeholder data**. This mapping is
the forward specification: it documents which API endpoint each UI component will call
when backend services are live.

---

## Principle 1 — Proxy-First API Access

The Next.js frontend never calls backend services directly from the browser. All API
calls are routed through Next.js Route Handlers (`/api/proxy/*`) running server-side.
This eliminates CORS requirements and allows server-side credential management.

```
Browser → Next.js Route Handler → Internal Service (cluster)
```

---

## Principle 2 — Read-Only UI, Write-Disabled Buttons

All write operations (Book Appointment, Emergency Dispatch, Consent Grant, Signoff
Approve) are rendered as disabled UI elements in the current shell. The integration
mapping records the target endpoint for each button so future activation is
straightforward.

---

## Principle 3 — Consent Gate Before Data Display

Any component displaying owner health data must verify consent before rendering:

```
1. Route Handler calls GET /v1/consent/{owner_id}/{scope_id}
2. If status != "granted" → render ConsentRequiredBanner, suppress data
3. If status == "granted" → fetch and render data
```

The consent check is performed server-side in the Route Handler, not client-side.

---

## Principle 4 — Role-Scoped Data Fetching

Each surface fetches only the data its role is permitted to see. The JWT passed to
backend services encodes the role. Services enforce scope on the server side; the UI
does not re-implement access control logic.

---

## Principle 5 — Fail-Safe Error Rendering

When a backend call fails or returns an error, the UI renders a degraded-but-safe state:

- Missing data → skeleton / placeholder (not blank)
- 403 Forbidden → role/consent error banner
- 5xx / timeout → service-unavailable notice with retry option
- No data from API → explicit "No records found" (not a spinner forever)

Exact error rendering per surface is specified in `shared/ERROR_RENDERING_MATRIX.md`.

---

## Principle 6 — No PII in URL Parameters

Owner/pet/principal identifiers passed in URL path or query params must be opaque UUIDs.
Human-readable names (owner name, pet name) must never appear in URLs.

---

## Principle 7 — Deferred Runtime Gaps Are Documented

Every surface has a `DEFERRED_RUNTIME_GAPS.md` listing UI components that require backend
work not yet delivered. These gaps are expected and do not constitute defects in the
current phase — they are the integration backlog.
