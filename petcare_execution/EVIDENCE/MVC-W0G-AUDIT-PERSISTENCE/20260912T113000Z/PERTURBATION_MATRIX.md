# A7 — perturbation matrix (Rule 17)

A perturbation result is believed only after the mutation is proven to have
landed. Verification is by **content diff and SHA-256**, not by `git diff`:
most probed files are new on this branch and untracked, and `git diff` reports
nothing for an untracked file — a check that falsely rejected five of six
probes in the W0-F lane before it was replaced.

For each probe: assert the target text exists → write the mutation → re-read
and assert the mutation is present and the original gone → assert a non-empty
content diff and a changed digest → only then run the control → restore the
exact original bytes, verified by digest → re-run.

| # | CONTROL | PERTURBATION | MARKER | DIFF | EXPECTED | ACTUAL | RESTORED |
|---|---|---|---|---|---|---|---|
| 1 | AUD-10 - a governed route must reach PostgreSQL persistence | `P-AUD-REPO-BYPASS` in `petcare_api/main.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (12 failed, 10 passed in 4.40s) | PASS |
| 2 | AUD-02 - a client-supplied tenant cannot override the session tenant | `P-AUD-TENANT` in `petcare_api/main.py` (5 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (5 failed, 17 passed in 6.67s) | PASS |
| 3 | AUD-03 - a client-supplied actor cannot become an authenticated actor | `P-AUD-ACTOR` in `petcare_api/main.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (3 failed, 19 passed in 4.35s) | PASS |
| 4 | AUD-04 - a client-supplied role can never match a real role | `P-AUD-ROLE` in `petcare_api/main.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 20 passed in 4.24s) | PASS |
| 5 | AUD-08 - a modified persisted row breaks verification | `P-AUD-VERIFY` in `petcare_api/audit_repository.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 20 passed in 4.28s) | PASS |
| 6 | AUD-06 - a tenant-scoped read cannot return another tenant's events | `P-AUD-XTENANT` in `petcare_api/audit_repository.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 20 passed in 4.82s) | PASS |
| 7 | AUD-12 - an unreachable store fails closed rather than dropping events | `P-AUD-SWALLOW` in `petcare_api/audit_repository.py` (5 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 21 passed in 4.30s) | PASS |

```
PERTURBATION_TOTAL=7
PROBE_MARKER_VERIFIED=7/7
DIFF_VERIFIED=7/7
CONTROL_FAILED_AS_REQUIRED=7/7
RESTORED_PASS=7/7
VACUOUS_CONTROLS=0
NO_EVIDENCE_RESULTS=0
```

The six required probe classes are all covered: repository bypass back to
in-memory (P-AUD-REPO-BYPASS), tenant from the request body (P-AUD-TENANT),
actor from the request body (P-AUD-ACTOR), role from the request body
(P-AUD-ROLE), hash verification bypass (P-AUD-VERIFY), and the postgres->memory
fallback class (P-AUD-SWALLOW, which is its audit-path equivalent: an
unreachable store silently returning success instead of raising). Cross-tenant
leakage is covered additionally by P-AUD-XTENANT.

## Probe hunks, verbatim

### P-AUD-REPO-BYPASS

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -227,3 +227,3 @@
     # indistinguishable from an action that never happened. The request fails.
-    stored = AUDIT_REPO.append_event(record)
+    stored = __import__("audit_repository").InMemoryAuditRepository().append_event(record)
     log.info("AUDIT %s", json.dumps(stored, default=str))
```

### P-AUD-TENANT

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -319,6 +319,3 @@
     """
-    try:
-        tenant_id = read_session(request).get("tenant_id") or UNATTRIBUTED_TENANT
-    except HTTPException:
-        tenant_id = UNATTRIBUTED_TENANT
+    tenant_id = payload.tenant_id or UNATTRIBUTED_TENANT
 
```

### P-AUD-ACTOR

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -326,3 +326,3 @@
         event_name=payload.event_name,
-        actor_id=f"{CLIENT_ASSERTED_PREFIX}{payload.actor_id or 'system'}",
+        actor_id=payload.actor_id or 'system',
         actor_role=f"{CLIENT_ASSERTED_PREFIX}{payload.actor_role}",
```

### P-AUD-ROLE

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -327,3 +327,3 @@
         actor_id=f"{CLIENT_ASSERTED_PREFIX}{payload.actor_id or 'system'}",
-        actor_role=f"{CLIENT_ASSERTED_PREFIX}{payload.actor_role}",
+        actor_role=payload.actor_role,
         tenant_id=tenant_id,
```

### P-AUD-VERIFY

```diff
--- petcare_api/audit_repository.py (original)
+++ petcare_api/audit_repository.py (probed)
@@ -139,3 +139,3 @@
     return {
-        "ok": result.ok,
+        "ok": True,
         "reason": result.reason,
```

### P-AUD-XTENANT

```diff
--- petcare_api/audit_repository.py (original)
+++ petcare_api/audit_repository.py (probed)
@@ -336,3 +336,3 @@
                 f"SELECT {_SELECT_COLUMNS} FROM audit_event "
-                "WHERE tenant_id = %s ORDER BY chain_seq LIMIT %s",
+                "WHERE (%s IS NOT NULL) ORDER BY chain_seq LIMIT %s",
                 (tenant_id, limit),
```

### P-AUD-SWALLOW

```diff
--- petcare_api/audit_repository.py (original)
+++ petcare_api/audit_repository.py (probed)
@@ -312,6 +312,3 @@
             # afterwards from one that never happened.
-            raise AuditWriteFailed(
-                f"the audit event could not be recorded ({type(exc).__name__}); "
-                "the action it describes must not be reported as successful"
-            ) from None
+            return dict(core)
 
```

