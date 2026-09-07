# MyVetiCare — continuation receipt, 2026-09-07

RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT

## Premise correction

The continuation instruction held PR #13 as HELD with an invalid P5, and W0-J as
unstarted. Neither was true — the prior transcript truncated mid-run.

```
PR #13 (W0-I)   MERGED 2026-09-07T10:23:53Z
PR #14 (W0-J)   MERGED 2026-09-07T10:41:26Z
```

The quoted line "P5 passed — that's a failure of my test, not a pass of my fix"
was the DIAGNOSIS, not the outcome. The signature guard was added in response and
P5 recorded FAILED before #13 merged. Re-verified at the head of this run.

C1 and C4 were therefore already satisfied. This run executed C2 and C3.

```
START_HEAD=e26c76ae997949a7bfcee5dbfd47bbdcc8cf532b
END_HEAD=38d632a900a46ae2c2cac9e35292328e80ddfdd9
```

## C1 — W0-I

```
W0I_STATUS=DELIVERED_AND_MERGED
W0I_PR=13 (merged 2026-09-07T10:23:53Z)

P5_RESULT=FAILED
  probe: restore tenant_id=None default on ProfessionalAuthorityRegistry.held_at
  failing control: test_tenant_id_carries_no_permissive_default
  reason: omission no longer raises TypeError under the perturbed implementation
P6_RESULT=FAILED
  probe: professional_class_at bypasses the shared tenant-scoped lookup
  failing control: test_t_prof_05b_professional_class_does_not_leak_across_tenants
P7_RESULT=FAILED
  probe: tenant matching removed from _grant_in_force
  failing controls: test_t_prof_05_authority_does_not_cross_tenants
                    test_t_prof_05b_professional_class_does_not_leak_across_tenants

T-PROF-05_RESULT=PASS  implemented as test_tenant_id_carries_no_permissive_default
                       (asserts no default on tenant_id; omission raises TypeError)
T-PROF-06_RESULT=PASS  implemented as test_t_prof_05_authority_does_not_cross_tenants
                       (tenant-A grant DENIED for tenant B)
T-PROF-07_RESULT=PASS  implemented as test_t_prof_05b_professional_class_does_not_leak_across_tenants
                       (foreign tenant resolves None)

W0I_SECURITY_REVIEW_DISPOSITION=BOTH_FINDINGS_FIXED_BEFORE_MERGE
  1 permissive tenant default (authorization bypass) -> tenant_id made required
  2 cross-tenant class inference -> both questions resolved by one _grant_in_force()
  plus the meta-finding: the original tests did not bind to the property, because
  every call site they wrote passed tenant_id explicitly. Closed by a signature
  assertion.
```

Control names differ from the instruction's numbering because they were written
before that numbering was issued. Semantics match one-for-one; the mapping is
recorded above rather than renaming merged code.

## C2 — tenant-scope sweep (PR #15)

```
W0G_TENANT_SWEEP=DEFECT petcare_api/main.py:283 — POST /audit/ui, unauthenticated,
  accepted a client-supplied tenant_id defaulting to "platform". Same defect W0-C
  removed from the tenant header, surviving in a second place and wearing a value
  instead of an absence. W0-G sharpened it: chained audit writes mean a forged
  event is correctly hashed and the chain verifies as VERIFIED, so the integrity
  proof lends the forgery credibility.
  FIXED: tenant_id removed from the payload model; tenant derives from the session
  or is UNATTRIBUTED; claimed actor_id/actor_role prefixed client-asserted: so no
  member of VALID_ROLES can match. 6 controls added.

W0H_TENANT_SWEEP=CLEAN — the static write-authority check operates over source and
  has no tenant dimension to omit; seller identity is carried by the parent record.

TENANT_STATIC_GUARD_RESULT=PASS
  tests/governance/test_tenant_scope_signatures.py
  1 allowlisted entry with a recorded reason: seed_user(tenant_id=None), a data
  constructor where None means "no tenant assignment" and require_tenant() fails
  closed on exactly that with 403 NO_TENANT_AUTHORITY.

TENANT_STATIC_GUARD_PERTURBATION=PASS
  planted tenant_id: Optional[str] = None        -> detected
  planted tenant_id: Optional[str] = "platform"  -> detected
  spellings tenant_id / tenantId / TENANT_ID / tenant -> all detected
  corrected form (tenant_id: str)                -> correctly NOT flagged

  NOTE: the guard as first written looked only for = None and would have MISSED
  the actual defect. A hard-coded scope is the same defect wearing a value.
```

## C3 — F3 retired-role needle (PR #15)

```
F3_NEEDLE_DISPOSITION=CASE_INSENSITIVE
  Underscore stays REQUIRED. Separator-optional matching was tried and matched the
  ordinary English phrase "pharmacy operator" across the governance prose — 18
  false positives, which would have driven the exclusion list to grow until the
  guard meant nothing. A wire role keeps its underscore; only its case drifts.

  Six occurrences were invisible to the case-sensitive guard and are now
  registered, including the whole GO_LIVE_CLOSURES/pharmacy_operator_confirmation/
  directory.

  ROLE_PHARMACY_OPERATOR = "Pharmacy Operator" remains IN COVERAGE. The exemption
  is TOKEN-WISE, not file-wise: file-wide exclusion was tried and blinded the guard
  inside those files — a planted PROBE_ROLE = "PHARMACY_OPERATOR" in main.py went
  undetected. Registered with the reason it confers nothing: excluded from
  VALID_ROLES, with test_t_disp_05_retired_pharmacy_operator_cannot_authenticate
  asserting that exclusion.

  Comments and docstrings are stripped before scanning; string literals are not.
  W0-D's own comment says "PHARMACY_OPERATOR is deliberately ABSENT", and a guard
  flagging that would be flagging the record of the retirement.

F3_PERTURBATION_RESULT=PASS
  probe A  PROBE_ROLE = "PHARMACY_OPERATOR"   in petcare_api     -> FAILED (caught)
  probe B  PROBE = "Pharmacy_Operator"        in petcare_runtime -> FAILED (caught)
  probe C  same string inside a # comment                        -> passed (correctly silent)
```

## C4 — W0-J

```
W0J_CLASSIFICATION=PARTIAL_SAFE_WORK_AVAILABLE (executed 2026-09-07, PR #14)
W0J_STATUS=DELIVERED_AND_MERGED
W0J_PR=14 (merged 2026-09-07T10:41:26Z)
  scrypt KDF (salted, memory-hard, work factors stored, rehash-on-next-login)
  six MVC-EXEC-001 §8 migration invariants enforced in CI, each perturbation-proven
  T-PW-01 armed (AST check on _hash_password calls, not a substring match)
  purpose limitation found ALREADY PRESENT, not re-ported
  GATED RESIDUE: persisted user store -> W0-F
```

## Wave-0

```
W0-A=DELIVERED   W0-B=DELIVERED   W0-C=DELIVERED   W0-D=DELIVERED   W0-E=DELIVERED
W0-F=ENGINEERING_HANDOFF_COMPLETE (agent implementation forbidden by the pack)
W0-G=DELIVERED with gated residue (chain persistence -> W0-F)
W0-H=DELIVERED with gated residue (seller population -> W0-F)
W0-I=DELIVERED (full — no residue)
W0-J=DELIVERED with gated residue (persisted user store -> W0-F)

WAVE0_DELIVERED_TOTAL=6/10 fully (A,B,C,D,E,I)

Not reported as 9/10 or 10/10. G, H and J each carry a real W0-F-dependent
residue, and W0-F's serving-layer replacement is Sponsor-side and outside the
agent boundary. Counting them as complete would misstate the estate.
```

## Regression — measured on merged main at 38d632a

```
REGRESSION_TOTALS
  governance + root (pytest tests)          174 passed
  serving API (pytest petcare_api/tests)     70 passed
  runtime (pytest petcare_runtime/tests)    247 passed
  web unit (vitest)                         120 passed
  typecheck (tsc --noEmit)                  clean
  responsive e2e (Playwright)                90 passed   RESPONSIVE=90/90
  TOTAL                                     701 green, 0 failed

  secret_scan.py               SCANNED=3810 ALLOWLISTED=0 FINDINGS=0  CLEAN
  prohibited_literal_scan.py   SCANNED=368  ACTIVE_LITERAL_DEFAULT=0
  verify_evidence_bundles.py   BUNDLES=20 ARTEFACTS=152 FAILED=0
  ASSERTIONS_WEAKENED=0
```

## Evidence

```
EVIDENCE_DIRS
  petcare_execution/EVIDENCE/MVC-W0F-READINESS/20260907T082004Z/
  petcare_execution/EVIDENCE/MVC-W0F-FINDINGS-DISPOSITION/20260907T091710Z/
  petcare_execution/EVIDENCE/MVC-W0G/20260907T093834Z/
  petcare_execution/EVIDENCE/MVC-W0H/20260907T095803Z/
  petcare_execution/EVIDENCE/MVC-W0I/20260907T101009Z/
  petcare_execution/EVIDENCE/MVC-W0J/20260907T103127Z/
  petcare_execution/EVIDENCE/MVC-TENANT-SWEEP-F3/20260907T110000Z/

EVIDENCE_HASHES (this run's bundle)
  f51e97bc5e2459737e9754e1aeb85b629552f0e89a387cc8e00a6325156e7c88  RUN_RECEIPT.md
  e06be44bffe0cb8c0f7bfb753f35502d6ec94be68a9948ae3543c0d044ddf172  REGRESSION_RESULTS.md

  All 20 bundles verify: BUNDLES=20 ARTEFACTS=152 FAILED=0
```

## Open findings and next gate

```
OPEN_FINDINGS
  1  I-2 migration invariant is enforced AS STAGED, which is an interpretation.
     Read literally it demands NOT NULL today, which would fail the W0-H migration
     CP-2 itself instructs be written additively, and would reward guessing seller
     values for historical rows. If the Sponsor reads I-2 strictly, the gate is one
     assertion to change. SPONSOR RULING INVITED.
  2  W0-G open question carried from CP-2, unresolved: whether ARCH-01 requires
     signatures or anchoring BEYOND the hash chain. The chain is WIRED, not
     COMPLETE — it does not defend against an actor who can rewrite every row and
     recompute every digest.
  3  Audit chain has no tenant dimension. /audit/events and /audit/chain/verify are
     platform-admin-gated and return the global chain; per-tenant audit
     verification is not currently possible. Design property, not a bypass.

NEXT_GENUINE_GATE
  W0-F serving-layer replacement — production datastore decision and residency
  D.21, both Sponsor-side. It gates the G/H/J residues and is forbidden to an agent
  lane by MVC-W0F-ENGINEERING-HANDOFF-001 (W0_F_AGENT_IMPLEMENTATION=NO).

NEXT_PROGRAMME_ACTION=WAVE0_SPONSOR_GATED_RESIDUALS_CLOSEOUT
```

## Stop predicate

```
C5 predicate 5 fired: all C1-C4 work is complete.
No C1 halt (P5 FAILED as required).
No C2 halt (no defect resisted two fix attempts; the one defect was fixed first try).
No live DB/apply, credential entry, dashboard config, incomplete-evidence merge, or
irreversible action was reached or attempted.

PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO
GCP_MUTATED=NO          EXTERNAL_DASHBOARD_MUTATED=NO
MIGRATIONS_APPLIED=NO   CREDENTIALS_MIGRATED=NO
```
