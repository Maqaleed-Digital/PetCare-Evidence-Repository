# UI Integration Mapping — Error Rendering Matrix

## Phase

PH-FND-4 · All petcare-web surfaces

## Purpose

Specifies how each HTTP error response from the backend is translated into a UI state.
All error rendering is implemented in the Next.js Route Handler layer before returning
a response to the client component.

---

## Standard Error-to-UI Mapping

| HTTP Status | Error Code                     | UI Rendering                                                              | User-Visible Text                              |
|-------------|--------------------------------|---------------------------------------------------------------------------|------------------------------------------------|
| 401         | `UNAUTHORIZED_*`               | Redirect to `/login` page                                                 | "Session expired. Please log in."              |
| 403         | `FORBIDDEN_INSUFFICIENT_ROLE`  | Role-error banner above affected component; component hidden              | "You do not have permission to view this."     |
| 403         | `FORBIDDEN_CONSENT_REQUIRED`   | Consent-required banner; data area shows locked state with scope label    | "Owner consent is required to view this data." |
| 403         | `FORBIDDEN_SCOPE_VIOLATION`    | Same as `FORBIDDEN_INSUFFICIENT_ROLE`                                     | "You do not have permission to view this."     |
| 404         | `NOT_FOUND_RESOURCE`           | Empty state illustration + "No records found" message                     | "No {resource} found."                         |
| 409         | `CONFLICT_STATE_TRANSITION`    | Inline error on the triggering button; toast notification                 | "This action is not available right now."      |
| 422         | `VALIDATION_*`                 | Field-level error messages below each failing input                       | Per-field: violation message from `violations[]` |
| 429         | `RATE_LIMITED_*`               | Toast notification with retry timer                                       | "Too many requests. Please wait {n}s."         |
| 500         | `INTERNAL_UNEXPECTED`          | Service-unavailable card with `request_id` shown for support              | "An unexpected error occurred. Ref: {request_id}" |
| 502         | `UPSTREAM_AUDIT_LEDGER`        | Service-unavailable card; write operation blocked                         | "Service temporarily unavailable."             |
| 503         | `UNAVAILABLE_*`                | Service-unavailable card with retry button                                | "Service temporarily unavailable. Retry?"      |
| Timeout     | (fetch timeout >8s)            | Skeleton replaced with timeout card                                       | "Request timed out. Check connection."         |
| Network err | (fetch throws)                 | Connection-error card; no crash                                           | "Could not reach the service."                 |

---

## Surface-Specific Error Overrides

### Emergency Surface

| Condition                                       | Override Rendering                                                      |
|-------------------------------------------------|-------------------------------------------------------------------------|
| `GET /v1/emergency/alerts` → 503                | Red banner: "ALERT SERVICE UNREACHABLE — contact on-call administrator" |
| Any emergency write → 403 / 502                 | Red inline error + do not dismiss automatically                         |

### Pharmacy Surface

| Condition                                        | Override Rendering                                   |
|--------------------------------------------------|------------------------------------------------------|
| `GET /v1/pharmacy/cold-chain/readings` → timeout | Amber banner: "Cold chain data unavailable — check sensors manually"   |
| Cold chain reading `normal: false`               | Amber row highlight (not an error — data-driven state) |

### Admin — Audit Viewer

| Condition                                        | Override Rendering                                   |
|--------------------------------------------------|------------------------------------------------------|
| `GET /v1/audit/events` → 403                     | "Audit access requires admin role. Contact your administrator." |
| `GET /v1/audit/events` → empty                   | "No audit events in selected range."                 |

---

## Consent Error Banner Component

The consent-error banner is a shared component rendered when `FORBIDDEN_CONSENT_REQUIRED`
is received. It displays:

1. The human-readable scope label (e.g., "Health Record Access")
2. The owner's name (pseudonymised if admin viewing; actual name if owner self-viewing)
3. A "Request Consent" deep-link (disabled in current read-only phase)

---

## Request ID Exposure

For 500-class errors, the `request_id` from the error envelope is rendered in small text
below the error message. This allows support to correlate the UI error with the
`audit_ledger` entry for the same request.
