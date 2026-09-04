# Current Cloud Run public reachability — anonymous probe with negative controls

**OBSERVED_AT:** 2026-09-03T20:49:35Z (UTC) · **Method:** anonymous HTTPS GET/HEAD only.
No credentials sent. No state-changing endpoint invoked. Raw capture: `anonymous_probe_raw.txt`.

## The instrument was validated before it was trusted

A `*.run.app` hostname resolves through a wildcard DNS record and is served by a
shared Google wildcard certificate. **Neither DNS resolution nor TLS success says
anything about whether a given service exists.** Both were confirmed identical on
a hostname invented for this run.

Three negative controls were probed alongside the targets:

| Probe | Host | GET / | Body SHA-256 (prefix) | Bytes |
|---|---|---|---|---|
| TARGET_API | `petcare-api-prod-232802712581.me-central2.run.app` | **500 → 503** | `f08cee02…` / `52f9a90f…` | 323 / 302 |
| TARGET_WEB | `petcare-web-prod-232802712581.me-central2.run.app` | **404** | `6b43b396…` | 272 |
| NEGCTL_SAMEPROJ | `zzz-nonexistent-mvc-probe-232802712581…` | 404 | `6b43b396…` | 272 |
| NEGCTL_FAKEPROJ | `zzz-nonexistent-mvc-probe-999999999999…` | 404 | `6b43b396…` | 272 |
| NEGCTL_RANDOM | `qq7x3v9k2mprobe-100000000001…` | 404 | `6b43b396…` | 272 |

All three controls return a **byte-identical** 404. That fixes the fingerprint of
*"no such Cloud Run service"* — `6b43b396…`, 272 bytes.

## Findings

**1. `petcare-web-prod` no longer exists.** It returns the negative-control 404,
byte-for-byte. It is indistinguishable from a name that never existed. The web
service recorded as PRODUCTION_ACTIVE in PH5.1 is gone.

**2. `petcare-api-prod` still exists as a service object.** It is the only probe
that is *not* the 404 fingerprint. Distinct status codes, distinct bodies.

**3. No application is serving on it.** Steady state across three repeats is
`503` on `/`, on `/health`, **and on randomly-generated paths**. A running
application would 404 an unknown route itself; a uniform 503 on every path means
requests never reach application code. The bodies confirm it — both are Google's
generic frontend error pages (`server: Google Frontend`, `content-type: text/html`),
carrying the strings "The server encountered an error" and **"The service you
requested is not available yet"**. That second string is Cloud Run's message for a
service with no healthy serving revision.

**4. No IAM denial was emitted.** A Cloud Run service without an `allUsers` invoker
binding answers an anonymous request with `403`. Across every probe and repeat, no
`401` or `403` was observed.

## Classification

```
ANONYMOUS_REQUEST_REACHED_GOOGLE_FRONTEND   = YES
ANONYMOUS_REQUEST_REACHED_APPLICATION_CODE  = NO      (frontend error page, not app output)
SERVICE_OBJECT_EXISTS (petcare-api-prod)    = YES     (discriminated by negative control)
SERVICE_OBJECT_EXISTS (petcare-web-prod)    = NO      (byte-identical to control 404)
CURRENT_RUNTIME_SERVING                     = NO      (503 on all paths incl. random)
CURRENT_RUNTIME_VULNERABLE                  = NO_CODE_EXECUTING
IAM_401_403_OBSERVED                        = NO
CURRENT_PUBLIC_NETWORK_REACHABILITY         = PROBABLE_NOT_PROVEN
```

### Why `PROBABLE`, and not `YES`

The absence of a `403` is meaningful — Cloud Run's invoker check is normally
enforced at the frontend, so a private service would deny an anonymous caller
regardless of container health. That is a real signal and it points at a public
invoker binding.

It is not proof. It cannot be excluded from outside that a service with **no
healthy revision short-circuits to 503 before the IAM check is applied**, in which
case the missing 403 is an artefact of the broken revision rather than evidence of
a public binding. Distinguishing these requires one read of the service IAM policy,
which is credential-gated (see `GCP_FORENSIC_READ_CARD.md`).

**A 500 is not evidence that a caller reached the application.** The earlier
reading — that a server-side result implies the request penetrated to service code
— does not survive inspection of the response body. It is a Google Frontend page.
