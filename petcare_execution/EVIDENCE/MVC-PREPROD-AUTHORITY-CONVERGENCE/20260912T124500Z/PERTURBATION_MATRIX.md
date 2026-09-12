# A21 — perturbation matrix (Rule 17)

Every control below was made to FAIL by a mutation proven to have landed, then
restored and re-run. A perturbation that cannot be shown to have applied is no
evidence — not a passing control.

| # | CONTROL | PERTURBATION | MARKER | DIFF | EXPECTED | ACTUAL | RESTORED |
|---|---|---|---|---|---|---|---|
| 1 | ROLE-03 - a display label is never an authority token | `P-ROLE-DISPLAY-AUTHORITY` in `petcare_api/roles.py` (1 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (8 failed, 23 passed in 1.23s) | PASS |
| 2 | PHARM-ROLE-04 - no pharmacy authority in the web allowlists | `P-PHARMACY-IN-ALLOWLIST` in `petcare_web/middleware.ts` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (3 failed, 42 passed in 1.59s) | PASS |
| 3 | SEED-01 - application startup creates zero identities | `P-SEED-USER-RESTORED` in `petcare_api/main.py` (3 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (5 failed, 11 passed in 2.85s) | PASS |
| 4 | SEED-02c - no credential-shaped literal in serving source | `P-DEFAULT-PASSWORD-RESTORED` in `petcare_api/main.py` (1 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 15 passed in 2.34s) | PASS |
| 5 | TENANT-01 - an unknown tenant assignment is denied | `P-TENANT-UNKNOWN-ACCEPTED` in `petcare_api/tenants.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (6 failed, 12 passed in 2.11s) | PASS |
| 6 | TENANT-04 - there is no default tenant | `P-FAKE-PLATFORM-TENANT` in `petcare_api/tenants.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 17 passed in 2.09s) | PASS |
| 7 | MIG-05 - a record with no tenant is quarantined, never assigned one | `P-MIGRATION-GUESSES-TENANT` in `scripts/governance/identity_migration_dryrun.py` (3 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (4 failed, 32 passed in 0.13s) | PASS |
| 8 | PERSIST-01 - postgres selected and unavailable must fail closed | `P-PERSIST-MEMORY-FALLBACK` in `petcare_api/persistence.py` (5 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (3 failed, 9 passed in 0.26s) | PASS |
| 9 | AUD-02 - a client-supplied tenant cannot override the session tenant | `P-AUDIT-CLIENT-AUTHORITY` in `petcare_api/main.py` (5 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (5 failed, 17 passed in 7.37s) | PASS |

```
PERTURBATION_TOTAL=9
PROBE_MARKER_VERIFIED=9/9
DIFF_VERIFIED=9/9
CONTROL_FAILED_AS_REQUIRED=9/9
RESTORED_PASS=9/9
VACUOUS_CONTROLS=0
NO_EVIDENCE_RESULTS=0
```

Every class the instruction required is covered: a display role accepted as
authority, pharmacy in an allowlist, a hardcoded seed user restored, a
hardcoded default password restored, an unknown tenant accepted, a fake
`platform` tenant default, a migration that guesses a tenant, a
postgres-to-memory fallback, and audit authority taken from client input.

## The harness itself was wrong twice, and both were caught by its own rules

**Insertion probes were falsely rejected.** Two probes prepend a line before a
marker, so the replacement text CONTAINS the original — and the marker rule
required the original to be gone. Both reported `probe did not land` having
landed perfectly. The rule now distinguishes an insertion from a replacement.

**A control could not see its own probe.** `P-DEFAULT-PASSWORD-RESTORED`
planted `DEFAULT_ADMIN_PASSWORD = "..."` and SEED-02c passed. Its matcher
carried a negative lookbehind meant to skip `password_hash`, which skipped
every credential-shaped name with an underscore in front of the word. The
control was fixed, then the probe made it fail. A perturbation that fails to
break a control is a finding about the control.

## Probe hunks, verbatim

### P-ROLE-DISPLAY-AUTHORITY

```diff
--- petcare_api/roles.py (original)
+++ petcare_api/roles.py (probed)
@@ -70,2 +70,3 @@
     ROLE_OWNER,
+    "Platform Admin", "Partner Clinic Admin", "Veterinarian", "Owner",
 })
```

### P-PHARMACY-IN-ALLOWLIST

```diff
--- petcare_web/middleware.ts (original)
+++ petcare_web/middleware.ts (probed)
@@ -49,3 +49,3 @@
   // gone because it is not a role.
-  '/account': ['owner', 'vet', 'clinic', 'admin'],
+  '/account': ['owner', 'vet', 'clinic', 'admin', 'pharmacy'],
 }
```

### P-SEED-USER-RESTORED

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -130,2 +130,5 @@
 # importing this module creates zero identities.
+
+seed_user("u-probe-001", "probe@test.invalid", "probe-seed-credential",
+          "platform_admin", "Probe Admin")
 
```

### P-DEFAULT-PASSWORD-RESTORED

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -81,2 +81,3 @@
 # ---------------------------------------------------------------------------
+DEFAULT_ADMIN_PASSWORD = "probe-default-credential"
 ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",")
```

### P-TENANT-UNKNOWN-ACCEPTED

```diff
--- petcare_api/tenants.py (original)
+++ petcare_api/tenants.py (probed)
@@ -180,3 +180,3 @@
         )
-    if not tenants.is_assignable(tenant_id):
+    if False and not tenants.is_assignable(tenant_id):
         raise TenantDenied(
```

### P-FAKE-PLATFORM-TENANT

```diff
--- petcare_api/tenants.py (original)
+++ petcare_api/tenants.py (probed)
@@ -173,3 +173,3 @@
     """
-    if tenant_id is None:
+    if tenant_id is None or tenant_id == "platform":
         return
```

### P-MIGRATION-GUESSES-TENANT

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

### P-PERSIST-MEMORY-FALLBACK

```diff
--- petcare_api/persistence.py (original)
+++ petcare_api/persistence.py (probed)
@@ -152,3 +152,6 @@
 
-    pool = open_pool(url)
+    try:
+        pool = open_pool(url)
+    except Exception:
+        return build_persistence({**env, PERSISTENCE_MODE_ENV_VAR: MODE_MEMORY})
     tenants = PostgresTenantRepository(pool)
```

### P-AUDIT-CLIENT-AUTHORITY

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -343,6 +343,3 @@
     """
-    try:
-        tenant_id = read_session(request).get("tenant_id") or UNATTRIBUTED_TENANT
-    except HTTPException:
-        tenant_id = UNATTRIBUTED_TENANT
+    tenant_id = payload.tenant_id or UNATTRIBUTED_TENANT
 
```

