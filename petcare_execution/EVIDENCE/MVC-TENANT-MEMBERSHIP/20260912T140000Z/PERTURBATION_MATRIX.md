# Perturbation matrix (Rule 17)

Every control made to FAIL by a mutation proven to have landed, then restored
and re-run. Verification is by content diff and SHA-256.

| # | CONTROL | PERTURBATION | MARKER | DIFF | EXPECTED | ACTUAL | RESTORED |
|---|---|---|---|---|---|---|---|
| 1 | the assignment API accepts no role input (TENANT_ASSIGNMENT != ROLE_ASSIGNMENT) | `P-MEM-ROLE-PARAMETER` in `petcare_api/main.py` (1 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 37 passed in 10.10s) | PASS |
| 2 | only platform_admin may change tenant membership | `P-MEM-AUTHORIZATION` in `petcare_api/main.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (5 failed, 34 passed in 8.54s) | PASS |
| 3 | the tenant that was LEFT records the departure (two-event model) | `P-MEM-SINGLE-EVENT` in `petcare_api/tenant_membership.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (4 failed, 35 passed in 8.72s) | PASS |
| 4 | unknown and disabled tenants fail closed | `P-MEM-TENANT-VALIDATION` in `petcare_api/tenant_membership.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (2 failed, 37 passed in 9.90s) | PASS |
| 5 | a failed change leaves neither the identity nor the log altered | `P-MEM-AUDIT-OUTSIDE-TXN` in `petcare_api/tenant_membership.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 38 passed in 9.63s) | PASS |
| 6 | no structured tenant transition is hidden in reason_code | `P-MEM-REASON-ENCODES-TENANT` in `petcare_api/main.py` (2 lines) | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (3 failed, 36 passed in 9.73s) | PASS |

```
PERTURBATION_TOTAL=6
PROBE_MARKER_VERIFIED=6/6
DIFF_VERIFIED=6/6
CONTROL_FAILED_AS_REQUIRED=6/6
RESTORED_PASS=6/6
VACUOUS_CONTROLS=0
```

Each probe is a way the ruling could be violated in practice: a role parameter
reintroduced, the authority relaxed from `require_admin` to any role, the
removal event dropped, tenant validation skipped, the audit moved outside the
transaction so a rollback cannot reclaim it, and the tenant transition encoded
into `reason_code`.

## Probe hunks, verbatim

### P-MEM-ROLE-PARAMETER

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -416,2 +416,3 @@
     reason: str
+    role: Optional[str] = None
 
```

### P-MEM-AUTHORIZATION

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -436,3 +436,3 @@
                           request: Request,
-                          role: str = Depends(require_admin),
+                          role: str = Depends(require_role),
                           x_correlation_id: str = Header(default="unset")):
```

### P-MEM-SINGLE-EVENT

```diff
--- petcare_api/tenant_membership.py (original)
+++ petcare_api/tenant_membership.py (probed)
@@ -219,3 +219,3 @@
         # 4 · removal, scoped to the tenant being LEFT.
-        if previous_tenant_id is not None:
+        if False and previous_tenant_id is not None:
             removal_id = audit.append_event_on(conn, _event(
```

### P-MEM-TENANT-VALIDATION

```diff
--- petcare_api/tenant_membership.py (original)
+++ petcare_api/tenant_membership.py (probed)
@@ -200,3 +200,3 @@
             ).fetchone()
-            if assignable is None:
+            if False and assignable is None:
                 raise TenantMembershipDenied(
```

### P-MEM-AUDIT-OUTSIDE-TXN

```diff
--- petcare_api/tenant_membership.py (original)
+++ petcare_api/tenant_membership.py (probed)
@@ -220,3 +220,3 @@
         if previous_tenant_id is not None:
-            removal_id = audit.append_event_on(conn, _event(
+            removal_id = audit.append_event(_event(
                 event_name=EVENT_MEMBERSHIP_REMOVED,
```

### P-MEM-REASON-ENCODES-TENANT

```diff
--- petcare_api/main.py (original)
+++ petcare_api/main.py (probed)
@@ -454,3 +454,3 @@
             actor_role=payload["role"],
-            reason=body.reason,
+            reason=f"{body.reason} [{body.tenant_id}]",
             correlation_id=x_correlation_id,
```

