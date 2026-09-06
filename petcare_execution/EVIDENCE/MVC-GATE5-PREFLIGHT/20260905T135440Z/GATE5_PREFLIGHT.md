# Gate-5 preflight — measured at this T0

Read-only throughout. Nothing was rewritten, force-pushed, deleted or
reconfigured. Blast-radius numbers are re-measured here as
`GATE5_RESUME_CONDITIONS.md` requires; the prior run's numbers were **not**
reused.

```
PRODUCTION_MUTATED = NO · LIVE_DB_MUTATED = NO · GCP_MUTATED = NO
IRREVERSIBLE_HISTORY_ACTION_PERFORMED = NO
REMOTE_MUTATED = NO
```

## Preconditions from GATE5_RESUME_CONDITIONS.md

| # | Precondition | Status | Evidence |
|---|---|---|---|
| 1 | Fingerprint guard merged to `main` | **MET** | PR #6 `MERGED` 2026-09-05T09:44:32Z, merge commit `24de5399`; `gh api …/commits/main` returns the same sha |
| 2 | `CURRENT_HEAD_TRACKED_PLAINTEXT = 0` | **MET** | `tests/governance/test_retired_key_absence.py` — **5 passed**, run against a working tree whose root tree `a46ee9f0…` is byte-identical to `origin/main` |
| 3 | Real retired key still rejected (out-of-band) | **NOT MET — requires the operator** | The probe needs the retired key material, which by design exists nowhere in the repository. It cannot be run from inside this session without reintroducing the value. |
| 4 | `HEAD_TREE_IDENTICAL = YES` for every ref | **NOT ESTABLISHABLE YET** | This is a property *of the rewrite*. No rewrite exists: the prior mirror was ruled invalid and discarded, and no replacement has been produced. |
| 5 | A post-rewrite green suite is not sufficient | **ACKNOWLEDGED** | Recorded as a standing constraint, not a check to pass. |

## Blast radius — re-measured, do not reuse

Introducing commit `5202bb5ffbd6b3085cdeedc68c5e9ea876a0dc96`
— *feat(api,auth): wire pilot auth router into deploying petcare_api*, 2026-05-23.

```
PUBLISHED_CARRYING_REFS = 6
  origin/gate-evidence-prep
  origin/m8-brand-cleanup
  origin/main
  origin/mvc-ux-wo-001
  origin/mvc-ux-wo-002-trust-surfaces
  origin/security/w0a-require-session-signing-key

LOCAL_ONLY_CARRYING_REFS = 8
  govern/canonical-repository-authority
  govern/denominator-inventory
  security/w0a2-fingerprint-guard          <-- new since the last measurement
  wave0/w0-a-remove-hardcoded-secret-fallback
  wave0/w0-b-session-bound-authorization
  wave0/w0-c-server-derived-tenant
  wave0/w0-d-dispensing-fail-closed
  wave0/w0-e-withdraw-unsupported-attestation

TAGS_CARRYING = 0
FORKS         = 0
OPEN_PRS      = 0
```

The published set is **6**, matching the authorized scope as last pruned.
`origin/govern/canonical-repository-authority`, listed in the original Gate-5
authorization record, has since been merged and deleted at the remote, so it is
no longer published. The local-only set has grown from 7 to **8**: merging PR #6
deleted `origin/security/w0a2-fingerprint-guard`, leaving its local branch
carrying. The authorization record's condition 5 names five local Wave-0 refs;
the transaction must in fact cover **eight** local refs, or the three
`govern/*` and `security/*` locals must be deleted first. **This is a scope
delta against the ratified authorization and needs a sponsor ruling.**

## Protection currently on `main` — read independently

```
REQUIRED_CHECK=verify · STRICT=true · ADMIN_ENFORCEMENT=true
ALLOW_FORCE_PUSHES=false · ALLOW_DELETIONS=false
```

Identical to the state condition 4 requires be restored after the purge.

## Execution capability

```
MIRROR_PRESENT            = YES  (/Users/waheebmahmoud/dev/gate5-mirror.git, 63 refs)
MIRROR_STATUS             = DISCARDED_INVALID — contains the rewrite that disarmed
                            the guard. Must never be pushed. Not fetched, not read
                            into, not reused. Delete before the next attempt.
GIT_FILTER_REPO_INSTALLED = NO
RETIRED_KEY_MATERIAL      = NOT_AVAILABLE_IN_SESSION (by design)
```

---

# APPENDED 2026-09-06 — mirror governance correction and blocker disposition

*Append-only. Nothing above this line has been altered.*

## Mirror governance correction

The `MIRROR_STATUS = DISCARDED_INVALID` line immediately above refers to the
**earlier** mirror. It does not describe the mirror that was eventually used.

- `DISCARDED_INVALID` referred to the earlier invalid mirror `tmp.ULizkXaVgX`.
- That earlier mirror **disarmed W0-A** and was **destroyed**. It was never
  pushed, and the prohibition on it stands.
- `~/dev/gate5-mirror.git` was the **second post-W0-A2 mirror**.
- It was **created after PR #6 merged**.
- Its **commit-map was based on `24de5399`**.
- **Main tree identity passed.**
- The **armed scanner showed old > 0 and rewritten = 0.**
- The **introducing commit was unreachable** from the rewritten refs.
- The **Sponsor explicitly accepted that mirror** for Gate-5 publication.
- The **Gate-5 Sponsor transaction used that accepted mirror successfully.**

## Disposition of the three blockers recorded above

**1. No authorizable plan exists (portfolio control plane).** Confirmed and
unchanged. A GitHub repository has no host identity receipt, so
`portfolio-mutate` cannot address it and no PLAN_ID or PLAN_SHA256 can exist.
The act proceeded under `SPONSOR_POLICY_SCOPED_GATE5_AUTHORIZATION` with
`PORTFOLIO_CONTROL_PLANE = NOT_APPLICABLE`. No portfolio host was touched at
any point. See `GATE5_AUTHORIZATION.md` in the closeout pack.

**2. Mirror status contradicted in writing.** Resolved by the correction above;
the Sponsor ruling was given.

**3. Local-ref scope delta.** Resolved by **reconciliation, not rewriting**. The
ratified authorization named five local Wave-0 refs; the measured local carrying
set was fourteen heads. Every local ref was moved by compare-and-swap to the SHA
the already-validated commit-map assigns it — no new history was created
locally, and no additional remote ref was mutated. Three fully-contained merged
branches were pruned after measurement. See `WAVE0_LOCAL_REF_RECONCILIATION.md`
and `LOCAL_PRUNING.md`.

## Precondition 3 — the out-of-band probe

Recorded above as **NOT MET — requires the operator**. It was subsequently
satisfied out-of-band and is recorded in
`petcare_execution/EVIDENCE/MVC-W0A2-FINGERPRINT-GUARD/20260905T093411Z/REAL_LITERAL_OOB_PROOF.md`:
`PROBE_REAL_LITERAL = REJECTED`, with `PROBE_INPUT_SHA256` matching the pinned
fingerprint.

## Outcome

```
GATE5_STATUS              = PURGE_COMPLETE_OWNED_REFS
PURGE_COMPLETE_OWNED_REFS = YES
RESIDUAL                  = refs/pull/1..6/head — anonymously fetchable, still carrying
```

Closeout evidence:
`petcare_execution/EVIDENCE/MVC-GATE5-HISTORY-PURGE/20260906T174530Z/`
