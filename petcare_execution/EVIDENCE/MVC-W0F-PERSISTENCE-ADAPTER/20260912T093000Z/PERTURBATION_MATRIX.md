# A15 — perturbation matrix (Rule 17)

A perturbation result is believed only after the mutation is proven to have
landed. An ineffective probe and a vacuous control are indistinguishable from
test output alone — the previous W0-F run nearly recorded a false
`CONTROL_VACUOUS` verdict for exactly that reason.

Verification here is by **content diff**, not by `git diff`. Most of the files
probed are new in this change and therefore untracked, and `git diff` reports
nothing for an untracked file — a harness using it would report `probe did not
land` for a probe that landed perfectly. That was observed on the first run of
this harness: five of six probes were falsely rejected before the check was
replaced.

| # | CONTROL | PERTURBATION | PROBE_MARKER_VERIFIED | DIFF_VERIFIED | EXPECTED | ACTUAL | RESTORED |
|---|---|---|---|---|---|---|---|
| 1 | PERSIST-01 — postgres selected and unavailable must fail closed | `P-PERSIST-01` in `petcare_api/persistence.py` (10 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (3 failed, 9 passed in 0.20s) | PASS |
| 2 | SEC-SECRET-05 — Parameter Store may never satisfy a secret | `P-SEC-SECRET-05` in `petcare_api/secret_provider.py` (1 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 62 passed in 0.44s) | PASS |
| 3 | SEC-SECRET-04 — a placeholder secret is denied | `P-SEC-SECRET-04` in `petcare_api/secret_provider.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (23 failed, 41 passed in 0.54s) | PASS |
| 4 | DB-05 — an unresolved identity cannot enter the authoritative table | `P-DB-05` in `petcare_runtime/migrations/0031_w0f_identity_session_persistence.sql` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 34 passed in 3.94s) | PASS |
| 5 | DB-08 — a foreign-tenant session cannot resolve | `P-DB-08` in `petcare_api/postgres_repositories.py` (4 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (8 failed, 27 passed in 4.30s) | PASS |
| 6 | AC7-07 on PostgreSQL — key rotation must still revoke everything | `P-SESSION-ROTATE-PG-01` in `petcare_api/routers/auth.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 11 passed in 3.80s) | PASS |

```
PERTURBATION_TOTAL=6
PROBE_MARKER_VERIFIED=6/6
DIFF_VERIFIED=6/6
CONTROL_FAILED_AS_REQUIRED=6/6
RESTORED_PASS=6/6
VACUOUS_CONTROLS=0
```

## Probe hunks, verbatim

### P-PERSIST-01

```diff
--- petcare_api/persistence.py (original)
+++ petcare_api/persistence.py (probed)
@@ -140,3 +140,11 @@
 
-    pool = open_pool(url)
+    try:
+        pool = open_pool(url)
+    except Exception:
+        return Persistence(
+            mode=MODE_MEMORY,
+            session_store=InMemorySessionStore(),
+            identities=InMemoryIdentityRepository(),
+            invites=InMemoryInviteCodeRepository(),
+        )
```

### P-SEC-SECRET-05

```diff
--- petcare_api/secret_provider.py (original)
+++ petcare_api/secret_provider.py (probed)
@@ -83,2 +83,3 @@
     AUTHORITY_ENVIRONMENT,
+    AUTHORITY_SSM_PARAMETER_STORE,
 })
```

### P-SEC-SECRET-04

```diff
--- petcare_api/secret_provider.py (original)
+++ petcare_api/secret_provider.py (probed)
@@ -137,3 +137,3 @@
         )
-    if stripped.casefold() in PLACEHOLDER_SECRET_VALUES:
+    if False and stripped.casefold() in PLACEHOLDER_SECRET_VALUES:
         raise SecretUnavailable(
```

### P-DB-05

```diff
--- petcare_runtime/migrations/0031_w0f_identity_session_persistence.sql (original)
+++ petcare_runtime/migrations/0031_w0f_identity_session_persistence.sql (probed)
@@ -100,3 +100,3 @@
     -- a real, governed state and must remain expressible.
-    CHECK (provenance <> 'IDENTITY_MIGRATION' OR tenant_id IS NOT NULL),
+    CHECK (provenance <> 'IDENTITY_MIGRATION' OR tenant_id IS NULL OR tenant_id IS NOT NULL),
 
```

### P-DB-08

```diff
--- petcare_api/postgres_repositories.py (original)
+++ petcare_api/postgres_repositories.py (probed)
@@ -265,6 +265,6 @@
                 "WHERE session_id = %s "
-                "  AND tenant_id IS NOT DISTINCT FROM %s "
+                "  AND (%s IS NOT NULL OR %s IS NULL) "
                 "  AND expires_at > %s "
                 "  AND (revoked_at IS NULL OR revoked_at > %s)",
-                (session_id, tenant_id, _to_db(now), _to_db(now)),
+                (session_id, tenant_id, tenant_id, _to_db(now), _to_db(now)),
             ).fetchone()
```

### P-SESSION-ROTATE-PG-01

```diff
--- petcare_api/routers/auth.py (original)
+++ petcare_api/routers/auth.py (probed)
@@ -499,3 +499,3 @@
     except BadSignature:
-        raise HTTPException(status_code=401, detail={"error": "INVALID_SESSION"})
+        payload = _serializer().loads_unsafe(token)[1]
     if not isinstance(payload, dict) or not payload.get("role"):
```

