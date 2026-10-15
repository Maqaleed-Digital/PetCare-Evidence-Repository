# MVC-EPC-D-001 v1.5 — Lane D unit D3a: J-V1 internal portion (onboarding + licence status, CV-12) — J-V1 UNCOUNTED

```
UNIT=D3a   AUTHORITY=R21.4 (D3 veterinarian journeys, ledger order), R18.4, R19.3   BASE=origin/main 26b6edf
JOURNEY=J-V1 "onboarding, licence status" (D0 inventory: partial/partial, "no licensing adapter")
```

## Counting — J-V1 and CV-12 stay UNCOUNTED (X-33)
J-V1 includes licence verification. Verification against the issuing authority's registry is the open external dependency
**X-33** (CP2, R19.3: "admin attestation is not regulator verification … no mock registry may count it"); the repository's
licensing-authority port fails closed. Under the R21 Phase 5 rule for X-33-blocked units, only the internal portion is built.
The spec is tagged **[J-V1-INTERNAL]** (report.mjs does not count it) and carries **no screen tag**: CV-12 is not counted while
its licence status can only be an attestation. Same treatment as [J-O8-COD] (R20.1) and [J-O9-INTERNAL] (R21.1).

## What is built
- `/vet/profile` (CV-12, ar/en), linked from `/vet` (`vet-open-profile`): the veterinarian's registered licences
  (GET /api/practitioners/me/licence) and whether a practitioner authority is in force (GET /api/practitioners/me/authority).
  SUBMITTED until verified; a MANUAL_STAFF verification reads as "verified by a named staff member (recorded attestation)",
  never as a registry check; a standing notice says registry verification is not available. A veterinarian with no clinic yet
  (no tenant) is shown NO authority in force (fail closed).
- No API change: onboarding (invite registration with licence), tenant assignment and MANUAL_STAFF verification are existing
  served routes (FR-05, W0-C).
- `tools/e2e_stack.py`: four SYNTHETIC single-use veterinarian invites (`E2E-VET-INVITE-<project>`; invites are seeded at startup
  only — no served route) and a per-run TOTP factor for the seeded platform administrator (tenant assignment and licence
  verification are SQ-3 operations), written only beside the run's outbox in TMPDIR, as the veterinarian's (D2g). The R19.4
  guard (`test_r19_4_step_up_seeding_unreachable.py`) still passes: no seeding reaches application source.

## Full-stack acceptance (each project separately, one worker, no concurrent backend run)
| PROJECT | [J-V1-INTERNAL] | J-O7 regression (e2e MFA file now holds two keys) |
|---|---|---|
| en-desktop | run 1 FAIL (spec setup: platform admin had no SQ-3 factor -> 403 MFA_ENROLMENT_REQUIRED; kept in `run1/`); run 2 PASS | PASS |
| ar-desktop | PASS | PASS |
| en-mobile | PASS | PASS |
| ar-mobile | PASS | PASS |

The spec: /register as a veterinarian with invite and licence -> /vet -> profile: SUBMITTED, no authority, registry notice;
platform admin (API, stepped up) assigns the clinic and verifies MANUAL_STAFF with a stated basis; new sign-in -> VERIFIED by
attestation (`data-method=MANUAL_STAFF`), authority in force, registry notice still shown; Arabic: no untranslated copy.

## Evidence
| Check | Result |
|---|---|
| backend, CI command | **1314 passed, 0 failed** |
| web vitest · tsc | **49 files / 252 passed** (3 new) · clean |
| perturbations (`perturb_epc_d_d3a_jv1.py`) | **4 ARMED / 0 VACUOUS** |
| R19.4 seeding guard + repository scanners | 22 passed |
| prohibited-literal / secret / evidence bundles | 0 / CLEAN / 32 bundles FAILED=0 |

## Counts
No count changes: J-V1 UNCOUNTED (X-33), CV-12 UNCOUNTED. No ledger X-row closes.
