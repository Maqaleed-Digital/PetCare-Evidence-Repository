# Run receipt — post PORT-07..10 continuation

**Date:** 2026-09-04 · **Branch:** `govern/canonical-repository-authority`
**Repository:** `Maqaleed-Digital/PetCare-Evidence-Repository` (PUBLIC)

## What happened

The PORT-07..10 branch was pushed, and the remote SHA verified equal to local
HEAD. Two gaps were then closed in repository code, and both turned out to be
the same defect wearing different clothes: **a check that cannot fail is not a
check that passed.**

- **CI.** PR #3 merged with an empty `statusCheckRollup` and that was read as
  green. Three workflow files existed and none could gate a pull request: two
  trigger only on `release: published`, and the third sits in a nested
  `.github/` directory that GitHub Actions never reads. See
  `CI_GAP_REMEDIATION.md`.
- **Authority residency.** `499` cannot be measured here, and the reason is a
  near-miss: AUTH-01/02/03 have `source_path`s that *resolve*, to the document
  that cites them. See `AUTHORITY_RESIDENCY_GAP.md`.

## Measured, not relayed

| Suite | Result |
|---|---|
| `pytest tests` | **112 passed** (78 governance) |
| `pytest tests petcare_runtime/tests petcare_api/tests` | **392 passed** |
| `npx vitest run` | **120 passed** (18 files) |
| `npx tsc --noEmit` | clean |
| `npx playwright test` | **90 passed / 90** |
| `verify_evidence_bundles.py` | 6 bundles, 31 artefacts, **0 mismatches** |
| `secret_scan.py` | 3651 files, 1 allowlisted, **0 findings** |
| `prohibited_literal_scan.py` | 355 python files, **0 active defaults** |

Governance grew 39 → 78: +15 CI contract, +13 authority residency,
+11 repository scanners.

## Three defects the remediation produced and caught

Recorded because each is an argument for testable scripts over shell one-liners.

1. The shell secret scan **matched its own regex** and failed on a repository
   containing no secrets.
2. Two of three initial allowlist entries **matched nothing** — dead weight that
   would have become a permanent blind spot.
3. The scanner's own test file **was a finding**: a literal private-key header
   written as a synthetic positive. The tempting fix would have blinded the
   scanner to the likeliest place for a pasted secret.

## Gates

```
MANDATORY_GATE_REACHED = GATE-3  (required status check on main)
ALSO OUTSTANDING       = GATE-5  (published-history purge)
PRODUCTION_MUTATED     = NO
LIVE_DB_MUTATED        = NO
GCP_MUTATED            = NO
EXTERNAL_DASHBOARD_MUTATED = NO
IRREVERSIBLE_ACTION_PERFORMED = NO
```

See `GATE_REGISTER.md` for the measured pre-state and the exact desired
configuration.
