# MVC-POST-CP2-RATIFICATION — repository convergence with ratified CP-2

**Base:** `443c337a4de33012da491ca0daf7c7dc2fceb17e`
**Scope:** NON_PRODUCTION_ONLY · evidence convergence only, no engineering change

This bundle **supersedes** the CP-2 status recorded in
`MVC-WAVE0-GOVERNANCE-COMPLETION/20260907T130000Z/`. That bundle is sealed and
hashed and is **not rewritten** — its `CP2_STATUS=PROPOSED` was true when written
and is now superseded rather than corrected away.

## CP-2 — verified live, not relayed

Re-read from the Portfolio Decision Log this run
(`page_last_edited_at 2026-09-07T12:52:53Z`):

```
Decision ID     MVC-CP2-ENGINEERING-AUTHORIZATION
Decision Ref    CP-2
Status          Ratified
Date Ratified   2026-08-31
Immutable Lock  __YES__
Notes contain   RATIFICATION_LODGED_2026-09-07 (decision date 2026-08-31, not re-dated)
Pack SHA-256    8c11c8b9…c473a1 — matches the local pack
```

Expected state matched exactly. No contradiction. The row is immutable and was
not mutated by this run.

**The Sponsor's resolution is better than the one this lane had prepared.** My
prepared mutation would have moved `Date Ratified` to 2026-09-07 and carried the
31 Aug decision date in `Notes`. The applied resolution does the reverse — keeps
the decision date in the date property and records the lodgement date in `Notes`.
That preserves both facts without repurposing a field away from its name, and it
leaves the register queryable by decision date rather than by lodgement date.

## Wave-0 — recorded conservatively

```
WAVE0_ENGINEERING=ALL_AVAILABLE_ENGINEERING_COMPLETE
WAVE0_CLEAN_PACKAGES=6/10
WAVE0_RESIDUE_PACKAGES=W0-G,W0-H,W0-J
WAVE0_RESIDUE_DEPENDENCY=W0-F
```

The earlier 10/10 closure claim is **not** resurrected. Six packages are
delivered without residue (W0-A, W0-B, W0-C, W0-D, W0-E, W0-I). Three carry a
W0-F-dependent residue. W0-F is at engineering handoff with agent implementation
forbidden by its own pack.

## Determinations carried forward unchanged

```
FORGED_HISTORY=NO_PERSISTED_HISTORY_EXISTED

  Narrower qualification preserved: this determination concerns PERSISTED,
  CHAINED audit history. Transient stdout traces may have existed; their absence
  is not claimed. petcare_api carries no database driver, is not deployed by any
  active surface, and no deployment ever carried the vulnerable-and-chained
  combination.
```

```
SPEC_V3_1=ANNEX_ONLY_BY_ORIGIN
SPEC_V3_1_LINEAGE=SETTLED
```

Sponsor ruling adopted, and it is the better classification. This lane recorded
`NOT_RECOVERABLE_FROM_AVAILABLE_AUTHORITATIVE_SOURCES`, which implies something
went missing. The evidence does not support that reading: the custody manifest
holds V3.0 full, V3.1 Annex K and V3.2 baseline; the lineage identifies V3.1 as
an annex issuance; and an independent all-ref git-history search found only
Annex K for V3.1. Nothing is missing. V3.1 was **issued** as an annex —
"successor to V3.0, create-only increment", V3.0 incorporated by reference.

The consequence for the denominator is unchanged: V3.2 Appendix T names a "SPEC
V3.1 namespace" mass that no full document supplies, so
`DENOMINATOR_STATUS=NOT_REPRODUCIBLE_MISSING_SOURCE` still stands and 499 remains
the measured denominator. What changed is the cause: a create-only annex by
design, not a lost artefact.

```
GITHUB_SUPPORT_STATUS=NOT_SENT
GITHUB_SUPPORT_SCOPE=refs/pull/1-6
```

Draft retained at `MVC-GATE5-HISTORY-PURGE/20260906T174530Z/GITHUB_SUPPORT_REQUEST.md`
(first line: "draft (not submitted)"). Nothing was submitted externally.
Submission remains Gate 3 — external dashboard.

## W0-F remaining Sponsor decisions — verified, not assumed

The instruction expected three categories. Verification against the W0-F pack,
CP-2 and current code finds **five open decisions and one now closed**.

### CLOSED since the pack was written

```
W0-F acceptance criterion 8 — "Password storage uses a memory-hard KDF; no bare
SHA-256 survives" — is SATISFIED. W0-J replaced _hash_password with salted,
work-factored scrypt plus a rehash-on-next-login path. Verified in
petcare_api/routers/auth.py. W0-F's remaining scope is smaller than its pack
states.
```

### DECISION 1 — production serving data-store

```
DECISION            Which persistent store backs the identity serving layer.
OPTIONS             Not yet governed. The pack fixes only what it must NOT be:
                    no SQLAlchemy create_all (the 32 real migrations are
                    canonical), and not GCP (RETIRED_HISTORICAL).
RECOMMENDED_DEFAULT NONE. Blocked upstream by Decision 2 — store placement
                    cannot be finalised before residency.
SPONSOR_AUTHORITY   Ruling naming the store and its region, issued AFTER D.21.
```

### DECISION 2 — D.21 data residency

```
DECISION            Which residency authority governs MyVetiCare identity and
                    clinical data, and therefore which region may hold it.
STATE               OPEN. The pack: "Store placement cannot be finalised before it."
OPTIONS             Not enumerated in governed authority.
RECOMMENDED_DEFAULT NONE — and a caution rather than a default. The AWS sweep
                    (W0A_AWS_REACHABILITY_DETERMINATION) shows sibling portfolio
                    projects in me-central-1 and eu-central-1, with nothing named
                    petcare in any region. me-central-1 is UAE. MyVetiCare is a
                    KSA product under PDPL, dated Jeddah. Portfolio precedent is
                    therefore NOT a safe default here: adopting the sibling region
                    would place KSA personal data outside KSA, which is the exact
                    question D.21 exists to answer.
SPONSOR_AUTHORITY   D.21 residency determination, with counsel where PDPL
                    cross-border transfer is engaged.
```

### DECISION 3 — governed secret source

```
DECISION            AWS Secrets Manager vs SSM Parameter Store for SECRET_KEY.
STATE               Deferred by the pack to "the MyVetiCare AWS architecture
                    decision".
OPTIONS             GOVERNED — exactly these two are named.
RECOMMENDED_DEFAULT AWS Secrets Manager, on the narrow ground that the value is a
                    session signing key requiring rotation, and Secrets Manager
                    provides managed rotation that Parameter Store does not.
                    Offered as a recommendation only; _require_secret_key() is
                    deliberately indifferent to which supplies the environment,
                    so the code does not force the choice.
SPONSOR_AUTHORITY   GATE_CREDENTIAL_ENTRY. Naming the store is a decision;
                    entering the secret is the gate.
```

### DECISION 4 — session revocation behaviour

```
DECISION            Whether W0-F introduces a server-side session store or a
                    previous-key acceptance list, and if so, what revocation path
                    replaces the property that is lost.
WHY IT IS A DECISION Today there is one key and no fallback list, so rotating the
                    key invalidates every session — revocation by rotation. A
                    server-side store or a previous-key list REMOVES that property.
                    The pack is explicit: "Whichever way it goes, it must be a
                    decision, not a side effect."
STATE               W0-F acceptance criterion 7, unmet. Currently: no jti, no
                    deny-list, no logout invalidation.
RECOMMENDED_DEFAULT NONE — it follows from Decision 1. A store makes a deny-list
                    cheap; no store makes rotation the only lever.
SPONSOR_AUTHORITY   Ruling recorded against AC-7, taken WITH Decision 1 rather
                    than after it.
```

### DECISION 5 — identity migration

```
DECISION            Whether and how to migrate live identity into the new store.
STATE               Irreversible. The pack requires a rehearsed rollback and a
                    restore TEST, "not just a backup" (AC-9).
RECOMMENDED_DEFAULT NONE. Note that today there are no persisted credentials —
                    the store is in-memory and re-seeded at startup — so the
                    migration's cost depends entirely on when it is taken. Taken
                    before any production identity exists, it is close to free.
SPONSOR_AUTHORITY   GATE_IRREVERSIBLE_ACTION plus GATE_LIVE_APPLY, with the
                    restore test evidenced before the apply.
```

### Ordering

```
D.21 (2) -> data-store (1) -> revocation (4) -> secret source (3) -> migration (5)
```

Decisions 1 and 4 should be taken together: the revocation answer is a
consequence of the store answer, and taking them apart is how a store arrives
with revocation as an unexamined side effect — the thing the pack warns against.

```
NEXT_SPONSOR_DECISION=D.21 data-residency disposition
```

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO      LIVE_DB_QUERIED=NO
GCP_MUTATED=NO          EXTERNAL_DASHBOARD_MUTATED=NO
CP2_ROW_MUTATED=NO (immutable; read-only verification)
SEALED_EVIDENCE_REWRITTEN=NO (prior bundle superseded, not edited)
```
