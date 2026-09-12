# A15 — perturbation matrix (Rule 17)

A perturbation result is believed only after the mutation is proven to have
landed. An ineffective probe and a vacuous control are indistinguishable from
test output alone — the previous W0-F run nearly recorded a false
`CONTROL_VACUOUS` verdict for exactly that reason.

Verification is by **content diff**, not by `git diff`. Most probed files were
untracked when the first set ran, and `git diff` reports nothing for an
untracked file: the harness falsely rejected five of six probes before the
check was replaced. That is the same false-negative shape Rule 17 exists to
prevent, pointing the other way.

For each probe: assert the target text exists → write the mutation → re-read
and assert the mutation is present and the original gone → assert a non-empty
content diff and a changed SHA-256 → only then run the control → restore the
exact original bytes, verified by SHA-256 → re-run.

| # | CONTROL | PERTURBATION | MARKER | DIFF | EXPECTED | ACTUAL | RESTORED |
|---|---|---|---|---|---|---|---|
| 1 | PERSIST-01 — postgres selected and unavailable must fail closed | `P-PERSIST-01` in `petcare_api/persistence.py` (10 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (3 failed, 9 passed in 0.20s) | PASS |
| 2 | SEC-SECRET-05 — Parameter Store may never satisfy a secret | `P-SEC-SECRET-05` in `petcare_api/secret_provider.py` (1 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 62 passed in 0.44s) | PASS |
| 3 | SEC-SECRET-04 — a placeholder secret is denied | `P-SEC-SECRET-04` in `petcare_api/secret_provider.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (23 failed, 41 passed in 0.54s) | PASS |
| 4 | DB-05 — an unresolved identity cannot enter the authoritative table | `P-DB-05` in `petcare_runtime/migrations/0031_w0f_identity_session_persistence.sql` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 34 passed in 3.94s) | PASS |
| 5 | DB-08 — a foreign-tenant session cannot resolve | `P-DB-08` in `petcare_api/postgres_repositories.py` (4 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (8 failed, 27 passed in 4.30s) | PASS |
| 6 | AC7-07 on PostgreSQL — key rotation must still revoke everything | `P-SESSION-ROTATE-PG-01` in `petcare_api/routers/auth.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 11 passed in 3.80s) | PASS |
| 7 | MIG-03 - a migration can never increase privilege | `P-MIG-03` in `scripts/governance/identity_migration_dryrun.py` (5 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (14 failed, 22 passed in 0.19s) | PASS |
| 8 | MIG-04 - a tenant outside the supplied map is quarantined | `P-MIG-04` in `scripts/governance/identity_migration_dryrun.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 35 passed in 0.08s) | PASS |
| 9 | MIG-05 - a record with no tenant is quarantined, never assigned one | `P-MIG-05` in `scripts/governance/identity_migration_dryrun.py` (3 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (4 failed, 32 passed in 0.10s) | PASS |
| 10 | MIG-06 - every side of a duplicate is quarantined | `P-MIG-06` in `scripts/governance/identity_migration_dryrun.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 34 passed in 0.09s) | PASS |
| 11 | MIG-07 - a dry run writes zero authoritative rows | `P-MIG-07` in `scripts/governance/identity_migration_dryrun.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 11 passed in 2.77s) | PASS |
| 12 | KSA-02 - no W0-F module names a hosting location | `P-KSA-02` in `petcare_api/persistence.py` (1 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (3 failed, 14 passed in 24.71s) | PASS |

```
PERTURBATION_TOTAL=12
PROBE_MARKER_VERIFIED=12/12
DIFF_VERIFIED=12/12
CONTROL_FAILED_AS_REQUIRED=12/12
RESTORED_PASS=12/12
VACUOUS_CONTROLS=0
NO_EVIDENCE_RESULTS=0
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

### P-MIG-03

```diff
--- scripts/governance/identity_migration_dryrun.py (original)
+++ scripts/governance/identity_migration_dryrun.py (probed)
@@ -72,3 +72,6 @@
 #: different one by editing a table.
-ROLE_MAP: Mapping[str, str] = {role: role for role in sorted(VALID_ROLES)}
+ROLE_MAP: Mapping[str, str] = {
+    role: ("platform_admin" if role == "owner" else role)
+    for role in sorted(VALID_ROLES)
+}
 
```

### P-MIG-04

```diff
--- scripts/governance/identity_migration_dryrun.py (original)
+++ scripts/governance/identity_migration_dryrun.py (probed)
@@ -234,3 +234,3 @@
         if tenant_map is not None:
-            mapped = tenant_map.get(tenant)
+            mapped = tenant_map.get(tenant, tenant)
             if mapped is None:
```

### P-MIG-05

```diff
--- scripts/governance/identity_migration_dryrun.py (original)
+++ scripts/governance/identity_migration_dryrun.py (probed)
@@ -231,4 +231,3 @@
         if tenant is None or not str(tenant).strip():
-            hold(rec, UNRESOLVED_NO_TENANT)
-            continue
+            tenant = "platform"
         if tenant_map is not None:
```

### P-MIG-06

```diff
--- scripts/governance/identity_migration_dryrun.py (original)
+++ scripts/governance/identity_migration_dryrun.py (probed)
@@ -186,3 +186,3 @@
             seen[key] = seen.get(key, 0) + 1
-    duplicates = {k for k, n in seen.items() if n > 1}
+    duplicates = set()
     recon.duplicate_emails = sorted(duplicates)
```

### P-MIG-07

```diff
--- scripts/governance/identity_migration_dryrun.py (original)
+++ scripts/governance/identity_migration_dryrun.py (probed)
@@ -481,3 +481,3 @@
     applied = None
-    if args.apply:
+    if args.apply or True:
         if not all(recon.checks.values()):
```

### P-KSA-02

```diff
--- petcare_api/persistence.py (original)
+++ petcare_api/persistence.py (probed)
@@ -117,2 +117,3 @@
     mode = current_persistence_mode(env)
+    _FALLBACK_HOST = "petcare-prod.abc123.eu-central-1.rds.example.com"
 
```

