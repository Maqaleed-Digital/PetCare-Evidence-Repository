# Legacy-GCP public reachability — bounded unauthenticated check

**OBSERVED_AT:** 2026-09-04T11:29:21Z–11:29:23Z (UTC)
**Method:** anonymous HTTPS GET only. No credentials sent. No `gcloud`. No IAM read.
No authentication attempted. No mutation. Raw capture: `public_reachability_raw.txt`.

This is **not** a GCP infrastructure lane. It is the single present-day test that can
fire the cloud-agnostic CP-2 exclusion-2 incident trigger, and nothing more.

## The instrument was validated before it was trusted

`*.run.app` resolves through wildcard DNS and is served by a shared Google wildcard
certificate, so neither DNS resolution nor TLS success discriminates a service that
exists from one that never did. Two invented control hostnames were probed alongside
the targets in the same run to fix the "no such service" fingerprint.

| Probe | Path | HTTP | curl rc | Bytes | Body SHA-256 (prefix) |
|---|---|---|---|---|---|
| TARGET_API `petcare-api-prod-232802712581.me-central2.run.app` | `/health` | **500** | 0 | 323 | `f08cee02…` |
| TARGET_WEB `petcare-web-prod-232802712581.me-central2.run.app` | `/api/health` | **404** | 0 | 272 | `6b43b396…` |
| NEGCTL_SAMEPROJ `zzz-nonexistent-mvc-probe-232802712581…` | `/health` | 404 | 0 | 272 | `6b43b396…` |
| NEGCTL_FAKEPROJ `zzz-nonexistent-mvc-probe-999999999999…` | `/health` | 404 | 0 | 272 | `6b43b396…` |

Both controls return a byte-identical 404 — `6b43b396…`, 272 bytes. That is the
fingerprint of *no such Cloud Run service*.

## Findings, held to what the responses support

**TARGET_WEB is byte-identical to the negative controls.** Same status, same length,
same body hash. It is indistinguishable from a hostname that never existed. This is
stronger than "404 at the tested path": the control discriminates, and TARGET_WEB
falls on the absent side of it. `SERVICE_OBJECT_EXISTS=NO`.

**TARGET_API is the only probe that is not the control fingerprint.** A distinct
status and a distinct body mean a service object is still addressable. The response
is Google's own frontend error page — `server: Google Frontend`,
`content-type: text/html`, "The server encountered an error and could not complete
your request." That is the *platform* answering, not application code. No JSON, no
application headers, nothing a `/health` handler would emit.

**No IAM denial was emitted.** No `401` and no `403` on any probe. That is a real
signal and it points at a public invoker binding — but it is not proof, because a
service with no healthy revision may short-circuit before the invoker check. Settling
that requires one read of the service IAM policy, which is credential-gated and
**parked behind PATHFINDER-002**. It is not attempted here and must not be.

## Classification — evidence only

```
API_HTTP                                    = 500
API_CURL_RC                                 = 0
WEB_HTTP                                    = 404
WEB_CURL_RC                                 = 0

PUBLIC_REACHABILITY (api)                   = NO_APPLICATION_RESPONSE
PUBLIC_REACHABILITY (web)                   = NO_SERVICE_OBJECT
ANONYMOUS_REQUEST_REACHED_GOOGLE_FRONTEND   = YES
ANONYMOUS_REQUEST_REACHED_APPLICATION_CODE  = NO
SERVICE_OBJECT_EXISTS (petcare-api-prod)    = YES
SERVICE_OBJECT_EXISTS (petcare-web-prod)    = NO   (byte-identical to control)
LEGACY_GCP_SERVING                          = NO
IAM_401_403_OBSERVED                        = NO
HISTORICAL_PUBLIC_IAM                       = UNRESOLVED_BEHIND_IDENTITY_WALL

CP2_EXCLUSION_2_TRIGGERED = NO_FROM_CURRENT_PUBLIC_REACHABILITY_CHECK
```

Neither endpoint returned HTTP 200. The incident stop does not fire. This says nothing
about the historical window — exclusion 2 remains `ACTIVE_NOT_FIRED`, and the
historical question stays parked, not answered.

## Consistency with the 2026-09-03 probe

`CURRENT_CLOUD_RUN_PUBLIC_REACHABILITY.md` recorded `f08cee02…` for TARGET_API on `/`
and `6b43b396…` for TARGET_WEB on 2026-09-03T20:49:35Z. Both hashes reproduce exactly
15 hours later on different paths. The state is steady, not transient.
