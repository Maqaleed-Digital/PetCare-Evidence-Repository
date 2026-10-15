# MVC-EPC-D-001 — D3a addendum: CI shared-stack defect found and fixed (one fix attempt)

```
UNIT=D3a   PR=#107   FAILED_RUN=38822688644 (head 3eb8ab6)   RECEIPT=2026-10-16-epc-d-d3a-jv1-licence-status.md (unchanged)
```

## What failed, and why
CI serves all four projects from ONE stack. `[J-V1-INTERNAL]` (ar-desktop) registers a new veterinarian and assigns them to the
shared e2e clinic; the later `[J-O5]` runs (ar-mobile, en-desktop, en-mobile) list the clinic's veterinarians and assert exactly
the seeded one -> 3 failed, 73 passed. The local acceptance runs could not see it: each per-project run starts a fresh stack.
J-O5 (a counted, unchanged spec) was not altered.

## Fix
The J-V1 spec ends by revoking the new veterinarian's clinic membership (`POST /api/admin/identities/{id}/tenant`,
`tenant_id: null`, stepped up, audited) — the governed revocation — so the shared clinic is left as the spec found it.

## Evidence after the fix
| Check | Result |
|---|---|
| CI-shaped run: ONE stack, all four projects, `jo5-booking` + `jv1-licence-status` in CI order (`ci-shape-shared-stack-jv1-jo5.json`) | **8 passed, 0 failed** |
| `[J-V1-INTERNAL]` each project separately, one worker | **4/4 PASS** (pre-fix series kept in `pre-cleanup/`; en-desktop spec-setup run 1 still in `run1/`) |

A working-tree accident during the re-run (a broken shell chain redirected empty output over the four committed pre-fix result
files) was reverted from git before they were moved to `pre-cleanup/`; the committed bytes are what is kept.
Finding D3A-CI-SHARED-STACK: specs that add clinic members or change shared clinic state must restore it (the J-V2 spec in D3b
already republishes a full week for the same reason).
