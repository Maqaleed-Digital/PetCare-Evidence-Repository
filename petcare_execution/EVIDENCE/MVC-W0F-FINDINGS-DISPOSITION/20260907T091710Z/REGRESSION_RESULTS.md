# Regression — full current estate

Measured on `govern/w0f-findings-disposition`, based on `main` at `e3d4885`.
Counts are measured, not copied from the W0-F pack.

| Suite | Command | Result |
|---|---|---|
| governance + root | `pytest tests -q` | **153 passed** |
| serving API | `pytest petcare_api/tests -q` | **51 passed** |
| runtime | `pytest petcare_runtime/tests -q` | **234 passed** |
| web unit | `npm run test` (vitest) | **120 passed** (18 files) |
| typecheck | `npx tsc --noEmit` | **clean** (exit 0) |
| responsive e2e | `npx playwright test` | **90 passed** |
| | **Total** | **648 green, 0 failed** |

`tests/` rose from 143 to **153**: the ten new governance assertions added here
(5 × F1 GCP custody, 5 × F2/F3 retired-role absence).

Responsive holds at **90/90**. No test was modified, skipped, weakened or marked
xfail: `ASSERTIONS_WEAKENED=0`.

## Scanners

```
secret_scan.py               SCANNED=3771 ALLOWLISTED=0 FINDINGS=0   SECRET_SCAN=CLEAN
prohibited_literal_scan.py   SCANNED=359  ACTIVE_LITERAL_DEFAULT=0
verify_evidence_bundles.py   BUNDLES=14 ARTEFACTS=130 FAILED=0
```

The retired-key fingerprint appears in three files by design — the W0-A2 guard
and its two tests compare against it. It is a SHA-256 fingerprint, not the key.

## Code changed

One live-source change in this PR:

```
petcare_runtime/src/petcare/auth/access_control.py   -2 lines
```

Two dead `assigned_pharmacy_operator_id` fields removed from `AccessContext` and
`ResourceContext`. Read by nothing, passed by no call site. `petcare_runtime` is
234 green before and after.
