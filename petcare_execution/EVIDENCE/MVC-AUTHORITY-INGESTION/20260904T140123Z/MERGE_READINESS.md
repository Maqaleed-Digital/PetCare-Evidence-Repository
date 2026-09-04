# Merge readiness — `govern/canonical-repository-authority` → `main`

**Assessed:** 2026-09-04 · **Head:** `32b4764d64bef6d3114ff4dcfa41119c5aee7c96`

```
MERGE_EVIDENCE_COMPLETE = YES
MERGE_PERFORMED         = NO
```

## Criteria

| Criterion | State | Evidence |
|---|---|---|
| required check `verify` active on `main` | ✅ | protection: `contexts:["verify"]`, `strict:true`, `admins:true` |
| remote `verify` green on this exact head | ✅ | run `33882300897`, `headSha 32b4764d…`, conclusion `success` |
| fail-closed verdict over the real rollup | ✅ | `ci_verdict()` → **PASS** on the live check-runs |
| branch up to date with `main` | ✅ | 0 behind / 37 ahead — see below |
| clean-clone validation | ✅ | 3679 tracked files, 0 untracked, 397 passed |
| secret scan | ✅ | 3678 files, 0 allowlisted, 0 findings |
| prohibited-literal scan | ✅ | 355 files, 0 active defaults |
| responsive | ✅ | 90 / 90 |
| PORT regression | ✅ | 397 python · 120 vitest · tsc clean |
| evidence bundles | ✅ | 8 bundles, 54 artefacts, 0 mismatches |
| authority state accurately represented | ✅ | attribution corrected; 2 guards added |
| no evidence claim depends on untracked material | ✅ | custody ∩ unversioned = 0 |

## The blocker that was found and cleared

`strict: true` requires a branch to be **up to date** with `main` before merging.
This branch was **1 behind / 36 ahead**: `origin/main` carried `204bd4cc`, the
PR #3 merge that landed W0-A, which this branch had reached independently via
`e98ee966` and then built W0-B and W0-C on top of. Fast-forward was not possible
and the merge would have been refused.

`origin/main` was merged in. The single overlapping file,
`petcare_api/routers/auth.py`, auto-merged: both sides require the session
signing key, and this branch's copy is a superset adding `read_session` (W0-B)
and identity-derived tenant scope (W0-C). Verified after the merge — both
`_require_secret_key` and `read_session` present, 0 active literal defaults,
397 passed, and `verify` green on the merge commit.

## Open governance exceptions — recorded, not blocking

| ID | Status | Why it does not block |
|---|---|---|
| `EPIC_IDENTIFIER_COLLISION` | OPEN | EP-06 means different things in the two repositories. Remediation is alias/namespace only; it touches no code on this branch. |
| `MANIFEST_CITES_UNVERSIONED_ARTEFACTS` | OPEN | Bounded and pinned at exactly 146, all build output, **zero overlap** with cited evidence. Known and measured, not unresolved. |

## Why the merge was not performed

No governance artefact expressly authorizes merge to `main` for this lane. The
authority seal's `does_not_authorize` list does not name it either way, and
absence of a prohibition is not an authorization.

The merge is therefore a **Sponsor act**, not a gate: this is not GATE-4, because
GATE-4 is merging with *incomplete* evidence and the evidence is complete. It is
simply a decision that has not been delegated.
