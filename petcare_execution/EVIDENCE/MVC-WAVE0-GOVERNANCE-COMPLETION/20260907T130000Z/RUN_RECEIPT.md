# MVC-WAVE0-GOVERNANCE-COMPLETION — verification run

**Base:** `38d632a900a46ae2c2cac9e35292328e80ddfdd9`
**Scope:** NON_PRODUCTION_ONLY · verification and constitutional completion

```
RULE_13=GREEN_CI_NECESSARY_NOT_SUFFICIENT
RULE_14=LIVE_REGISTER_OUTRANKS_TRUNCATED_TRANSCRIPT
RULE_15=WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN
```

## A0 — live state, verified not relayed

All six PRs confirmed MERGED from GitHub, with merge commits:

```
PR#10 2026-09-07T09:26:04Z  200b169558ae0fa30990420e8d4590a9729ed2e8
PR#11 2026-09-07T09:48:00Z  6a0c315549d33582ff41a06dcc18b60c0a0a7946
PR#12 2026-09-07T10:04:20Z  4ed4469cde59b6fbd7b07d0811a978d68b1f648f
PR#13 2026-09-07T10:23:53Z  28c4f45d2f7151cba174db1ebd8a2ea41b538c9f
PR#14 2026-09-07T10:41:26Z  e26c76ae997949a7bfcee5dbfd47bbdcc8cf532b
PR#15 2026-09-07T12:01:11Z  38d632a900a46ae2c2cac9e35292328e80ddfdd9
origin/main = 38d632a900a46ae2c2cac9e35292328e80ddfdd9
```

### The one contradiction with the expected state, reported not overwritten

The instruction expects `WAVE0_ENGINEERING_DELIVERED=10/10`. The measured
position is **6/10 delivered without residue** (A, B, C, D, E, I), with G, H and
J each carrying a W0-F-dependent residue, and W0-F itself at engineering handoff
with agent implementation forbidden by its own pack.

Both statements can be true under different definitions, and the difference is
worth keeping rather than collapsing:

- **All available engineering work is done.** No safe, non-gated engineering step
  remains in any of the ten packages. In that sense the engineering lane is
  complete across 10/10.
- **Three packages are not fully delivered.** W0-G's chain is not persisted,
  W0-H's seller identity is not populated, W0-J's user store is not persisted.
  Each waits on W0-F's serving-layer replacement, which is Sponsor-side.

This record therefore states both, and does not report 10/10 delivered without
qualification.

## A1 — CP-2 ratification: PREPARED, NOT APPLIED

The canonical row was located and is unique:

```
Decision ID   MVC-CP2-ENGINEERING-AUTHORIZATION
Decision Ref  CP-2
Location      Portfolio Decision Log (Immutable)
Page id       3d23ed7d-c104-81ff-bf8c-ee37392aea5d
Current       Status=Proposed · Date Ratified=2026-08-31 · Immutable Lock=NO
Pack SHA-256  8c11c8b9…c473a1 — re-verified against the local pack, MATCHES
```

**The update was blocked by this session's permission classifier and was NOT
applied.** It is not deferred by my judgment — the Sponsor authority is explicit
and the act would otherwise have proceeded.

The exact intended mutation, unchanged, for a human to apply or approve:

```
Status                  Proposed -> Ratified
date:Date Ratified      2026-08-31 -> 2026-09-07
Immutable Lock          NO -> YES
Decision Title          "... — Sponsor decision taken 31 Aug 2026, ratified 7 Sep 2026"
Notes                   records BOTH dates explicitly, states CP-2 was NOT
                        formally ratified on 31 Aug, preserves scope and pack SHA
```

Two schema facts drove those choices:

1. `Date Ratified` is the **only** date property in this database. The
   instruction's carve-out — *"unless the existing governance schema uses another
   explicit field"* — has no other field to use, so the ratification date goes
   there and the 31 Aug authorization date is preserved in `Notes` and the page
   body. Leaving the property at 31 Aug while flipping Status would assert CP-2
   was ratified on 31 Aug, which the Sponsor expressly forbade.
2. The schema states *"Immutable Lock: always TRUE for Ratified entries"*.
   `~/.claude/CLAUDE.md` already flags DL-080 as unresolved precisely because its
   Notes read UNLOCKED while its Status reads Ratified. Ratifying without the
   lock would create a second instance of that defect.

```
CP2_STATUS=PROPOSED (unchanged — mutation blocked, not declined)
```

## A2 — prior receipt recovered

```
RECEIPT_EXISTS=YES
RECEIPT_SHA256=6444be3960fae5b69c8f72659b90b3bca19f9c42129253b8fc0b4408060e1651
```

All requested fields present; none ABSENT. It was untracked on disk and is
committed by this run so it survives the working tree.

## A3 — forged-history determination

```
FORGED_HISTORY_DETERMINATION=NO_PERSISTED_HISTORY_EXISTED
```

The question: before the `/audit/ui` write-authority correction, did any event
written with client-supplied tenant/actor/role become persisted, chained history?

Five independent facts, each verifiable from the repository:

1. **`petcare_api` cannot persist anything.** `requirements.txt` is
   `fastapi · uvicorn · pydantic · itsdangerous · passlib` — no database driver.
   A tree-wide search for `sqlite3|psycopg|create_engine|SQLAlchemy|DATABASE_URL`
   across `petcare_api/**.py` returns **zero** hits.
2. **`_audit()` writes to two places only** — `_audit_log.append(record)`, an
   in-memory list that dies with the process, and `log.info`, stdout.
3. **`petcare_api` is not deployed by any active surface.** `render.yaml` deploys
   `petcare_execution/scripts/petcare_min_runtime.py`. `petcare_api` appears in
   `.github/workflows/` only as a **test** target.
4. **Migration 0028 (the chain columns) was never applied.** No active surface
   runs migrations at all.
5. **No deployment ever carried the vulnerable-and-chained combination.** The
   chaining landed on `main` at 09:48:00Z (PR #11) and the fix at 12:01:11Z
   (PR #15). For a deployment to carry both, something must have deployed `main`
   inside that window. Nothing deploys `petcare_api` at all, and the GCP lane is
   recorded as *"a service with no healthy revision on a cloud that is no longer
   the target"*.

Stated honestly rather than as an absolute: a forged probe **would** have
appeared in stdout application logs. Application logs are not the chained audit
store, carry no chain, and are not the history this question is about — but they
are not nothing, and the distinction is recorded rather than glossed.

No live database was queried; none needed to be.

## A4 — seed_user allowlist bound to a fail-closed control

An equivalent test already existed, so it was reused rather than duplicated, per
instruction:

```
SEED_USER_ALLOWLIST_TEST=
  petcare_api/tests/test_tenant_authority.py::test_t_ten_02_identity_without_tenant_assignment_fails_closed
```

It exercises the real authorization path — a session carrying no tenant driving
an actual route, asserting `403 NO_TENANT_AUTHORITY` — not a source inspection.

The allowlist rationale now names it as `BOUND TO: <path>::<test>`, and a new
guard (`test_allowlist_binding_tests_exist_and_are_named`) asserts every
allowlist entry names a binding test that still exists. An exemption justified by
prose alone decays the moment the behaviour changes; one bound to a test fails
with it.

```
SEED_USER_PERTURBATION_RESULT=FAILED_AS_REQUIRED
  probe: require_tenant() null-tenant branch weakened to default "platform"
  -> test_t_ten_02 FAILED
  restored -> test_t_ten_02 PASSED; tenant static guard 7 passed
```

## A5 — Wave-0 completion record: NOT CREATED

The instruction gates this on CP-2 being Ratified. It is not, because the
mutation was blocked. Recording governance completion now would be exactly the
thing the instruction forbids — calling engineering delivery a governance
closure before its precondition holds.

```
WAVE0_ENGINEERING_DELIVERY=ALL_AVAILABLE_ENGINEERING_COMPLETE
  (6/10 without residue; G/H/J carry W0-F-dependent residue; F at handoff)
WAVE0_GOVERNANCE_COMPLETION=PENDING_CP2_RATIFICATION
```

## A6 — SPEC V3.1

```
SPEC_V3_1=NOT_RECOVERABLE_FROM_AVAILABLE_AUTHORITATIVE_SOURCES
```

Verified independently rather than relayed from the lineage record:

- `git log --all --diff-filter=A` across the entire history returns exactly one
  matching artefact — `MVC-SPEC-001_V3_1_Annex_K_Split_Taxpayer_Requirements.md`.
  No full V3.1 document was ever added on any ref.
- `find ~/Maqaleed` returns only V3.0 and the V3.1 Annex K.

What exists, and its lineage:

```
MVC-SPEC-001 V3.1 · Annex K — Split-Taxpayer Requirement Groups (ARCH-05)
  SHA-256   058356cc916f9a274315bf19e6e6cbb0d9a20e0c2bc69d471cf94a87d6461c3b
  Version   V3.1 — successor to V3.0, CREATE-ONLY INCREMENT
  Predecessor  V3.0 (SHA-256 a3f2fb2c…3a19) incorporated by reference, unmutated
  Authority    Sponsor decision D-2R, 30 Aug 2026
  Status       DRAFT — pending Sponsor verdict. Not ratified.
```

So V3.1 is not a lost document so much as a version that exists **only** as a
create-only annex over V3.0. The gap it leaves is specific and already named in
`DENOMINATOR_RECONCILIATION.md`: V3.2 Appendix T derived its set from *"the BRD
V3.1 S0–S10 part structure and the SPEC V3.1 / GAP V1.7 namespaces"*, and one of
those two namespace sources has no document behind it. Two further historic-run
inputs are also absent and were never committed — the inventory JSON that
`mvc_content_completeness.py` consumes, and six `.txt` conversions.

`DENOMINATOR_STATUS = NOT_REPRODUCIBLE_MISSING_SOURCE` therefore stands, and 499
remains the measured denominator.

```
SPEC_V3_1_NEXT_ACTION=SPONSOR_DECLARATION
  Declare that MVC-SPEC-001 V3.1 comprises Annex K as a create-only increment
  over V3.0 (incorporated by reference), that no full-text V3.1 exists or has
  ever existed in custody, and that the 500-denominator reconstruction is
  permanently not reproducible for that reason. No historical content is
  fabricated to close it.
```

## A7 — Gate-5 refs/pull residual

```
GITHUB_SUPPORT_STATUS=NOT_SENT
  evidence: petcare_execution/EVIDENCE/MVC-GATE5-HISTORY-PURGE/20260906T174530Z/
            GITHUB_SUPPORT_REQUEST.md — line 1 reads
            "# GitHub Support request — draft (not submitted)"
  The 7 Sep session handoff records "Send status UNKNOWN"; the repository
  artefact is the more specific evidence and says draft, not submitted.

GITHUB_SUPPORT_NEXT_ACTION=GATE_EXTERNAL_DASHBOARD
  The draft and its evidence references are complete. Submission requires an
  authenticated GitHub Support interaction, which is an external dashboard act
  and was not attempted. Gate-5 itself is NOT reopened; this is residual
  public-discoverability remediation only.
```

## A8 — lost corrections

Both recovered from durable committed evidence, not reconstructed from memory:

```
LOST_CORRECTION_1=RECOVERED
  "Measured against a stale local main; the orphaned PORT citations were not a
  live defect — Gate-5 closure had already re-anchored them."
  source: petcare_execution/EVIDENCE/MVC-W0F-READINESS/20260907T082004Z/RUN_RECEIPT.md
  also carried in the PR #9 description.

LOST_CORRECTION_2=RECOVERED
  "policy_enforcer.ts is a stale design artefact, NOT a live authorization
  grant — nothing under petcare_execution compiles or runs."
  source: petcare_execution/EVIDENCE/MVC-W0F-FINDINGS-DISPOSITION/20260907T091710Z/
          F3_POLICY_ENFORCER_DISPOSITION.md
  also carried in the PR #10 description.
```

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO      LIVE_DB_QUERIED=NO
GCP_MUTATED=NO          EXTERNAL_DASHBOARD_MUTATED=NO
MIGRATIONS_APPLIED=NO   NOTION_REGISTER_MUTATED=NO (blocked, not declined)
```
