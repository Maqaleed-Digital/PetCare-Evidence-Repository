# Receipt - first `platform_admin` genesis mechanism (non-production)

**Date:** 2026-09-12 · **Authority:** `MVC-GENESIS-PLATFORM-ADMIN-001` section 8 `[SPONSOR]`
**Repository:** `petcare-evidence-repository`, branch `govern/platform-admin-genesis`
**Evidence:** `petcare_execution/EVIDENCE/MVC-GENESIS-PLATFORM-ADMIN/20260912T160000Z/`
**Governance:** `RATIFICATION-004.md` · prepared step `P1_GENESIS_STEP-001.md`

```
GENESIS_NON_PRODUCTION_IMPLEMENTATION=COMPLETE
FIRST_PLATFORM_ADMIN_BOOTSTRAP_AUTHORITY=RULED
PRODUCTION_GENESIS_EXECUTED=NO
GENESIS_CONSUMED=NO
PRODUCTION_TENANT_ROW_CREATED=NO
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
```

Regression **889 passed** (baseline 854), each suite also run alone
(271 / 371 / 247). 35 new controls: 18 on real PostgreSQL, 17 governance
guards. Perturbation **ARMED=13/13, VACUOUS=0**.

Two perturbations needed a second pass. Removing either single-use precondition
from the service left both controls passing; stripping the deeper layers showed
the durable constraints and the post-write invariant are what hold. Recorded in
full in `PERTURBATION_MATRIX.md`, because the first answer was wrong and the
correction is the finding.

One harness defect fixed: `reset_w0f_tables` did not empty
`platform_admin_genesis`, and the FK onto `user_identity` made every suite
sharing the session database error in teardown.

Next gate is unchanged: `GATE_LIVE_APPLY` for P1 phases B-D. The genesis step is
prepared and separately gated; it is not covered by the B-D authorization
request.
