# Perturbation matrix (Rule 17)

| # | CONTROL | PERTURBATION | MARKER | DIFF | EXPECTED | ACTUAL | RESTORED |
|---|---|---|---|---|---|---|---|
| 1 | the ruled tenant identifier appears in no creating code | `P-TENANT-ID-IN-SERVING-CODE` in `petcare_api/tenants.py` | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 7 passed in 0.15s) | PASS |
| 2 | no migration creates a tenant row without authorization | `P-TENANT-ROW-IN-MIGRATION` in `petcare_runtime/migrations/0034_pre1_tenant_registry.sql` | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (3 failed, 5 passed in 0.24s) | PASS |
| 3 | the ruling is recorded in governance (the guard is two-sided) | `P-RULING-NOT-RECORDED` in `petcare_execution/GOVERNANCE/MVC-PREPROD-SPONSOR-DECISION-001/RATIFICATION-003.md` | YES | YES | CONTROL_FAILS | CONTROL_FAILED_AS_REQUIRED (1 failed, 7 passed in 0.14s) | PASS |

```
PERTURBATION_TOTAL=3
CONTROL_FAILED_AS_REQUIRED=3/3
RESTORED_PASS=3/3
VACUOUS_CONTROLS=0
```

## A probe that landed and proved nothing

`P-RULING-NOT-RECORDED` first ran as a single-occurrence replacement. The
marker and the diff both verified — the mutation landed — and the control
still passed, which the harness reports as `CONTROL IS VACUOUS`.

It was not vacuous. The ruled identifier legitimately appears **twice** in the
ratification record (once in the structured outcome, once in the verbatim
Sponsor statement), so removing one occurrence left the property the control
tests intact. An INEFFECTIVE PROBE and a VACUOUS CONTROL are indistinguishable
from test output alone, which is the whole reason Rule 17 exists — and here the
harness's own verdict was the misleading one.

The harness now supports `replace_all` for exactly this shape, with the marker
rule tightened so a replace-all probe must leave NO occurrence behind. Re-run,
the control failed as required.

## Probe hunks, verbatim

### P-TENANT-ID-IN-SERVING-CODE

```diff
--- petcare_api/tenants.py (original)
+++ petcare_api/tenants.py (probed)
@@ -54,2 +54,3 @@
 
+DEFAULT_TENANT = "pharmacare_riyadh"
 TENANT_ACTIVE = "ACTIVE"
```

### P-TENANT-ROW-IN-MIGRATION

```diff
--- petcare_runtime/migrations/0034_pre1_tenant_registry.sql (original)
+++ petcare_runtime/migrations/0034_pre1_tenant_registry.sql (probed)
@@ -57,2 +57,3 @@
 
+INSERT INTO tenant (tenant_id, display_name) VALUES ('pharmacare_riyadh', 'Pharma Care');
 ALTER TABLE user_identity
```

### P-RULING-NOT-RECORDED

```diff
--- petcare_execution/GOVERNANCE/MVC-PREPROD-SPONSOR-DECISION-001/RATIFICATION-003.md (original)
+++ petcare_execution/GOVERNANCE/MVC-PREPROD-SPONSOR-DECISION-001/RATIFICATION-003.md (probed)
@@ -10,3 +10,3 @@
 ITEM_2_STATUS=RESOLVED
-ITEM_2_TENANT_ID=pharmacare_riyadh
+ITEM_2_TENANT_ID=<redacted-by-probe>
 ITEM_2_DISPLAY_NAME=Pharma Care Pharmacies — Riyadh
@@ -28,3 +28,3 @@
 >
-> tenant_id = pharmacare_riyadh
+> tenant_id = <redacted-by-probe>
 > display_name = Pharma Care Pharmacies — Riyadh
```

