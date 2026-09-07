# MVC-TENANT-SWEEP-F3 — tenant-scope assurance sweep and F3 needle repair

**Authority:** MVC-GOV-CANON-001 · W0-C · W0-I security review
**Base:** `e26c76ae997949a7bfcee5dbfd47bbdcc8cf532b`
**Scope:** NON_PRODUCTION_ONLY · findings lane, not a package reopening

## A correction to the premise this lane was opened on

The continuation instruction held PR #13 as HELD with an invalid P5, and W0-J as
unstarted. Neither is the case — the transcript truncated mid-run.

```
PR #13 (W0-I)  MERGED 2026-09-07T10:23:53Z
PR #14 (W0-J)  MERGED 2026-09-07T10:41:26Z
```

The P5 result the instruction quotes — *"P5 passed — that's a failure of my test,
not a pass of my fix"* — was the diagnosis, not the outcome. The signature guard
`test_tenant_id_carries_no_permissive_default` was added in response, and P5 was
re-run and recorded FAILED before #13 merged. Re-verified again at the head of
this run:

```
P5  restore tenant_id=None default  -> FAILED
      test_tenant_id_carries_no_permissive_default
    restored                        -> 13 passed
```

The three controls the instruction specifies as T-PROF-05/06/07 all exist, under
names chosen before the canonical numbering was issued:

| Instruction | Implemented as | Property |
|---|---|---|
| T-PROF-05 | `test_tenant_id_carries_no_permissive_default` | omission raises `TypeError`; no default on the signature |
| T-PROF-06 | `test_t_prof_05_authority_does_not_cross_tenants` | tenant-A grant denied for tenant B |
| T-PROF-07 | `test_t_prof_05b_professional_class_does_not_leak_across_tenants` | foreign tenant resolves `None` |

C1 and C4 were therefore already satisfied. This lane executes C2 and C3, which
were not.

## C2 — tenant sweep

```
W0G_TENANT_SWEEP=DEFECT petcare_api/main.py:283 unauthenticated /audit/ui accepted a
  client-supplied tenant_id defaulting to "platform"
W0H_TENANT_SWEEP=CLEAN
```

### The W0-G defect

`POST /audit/ui` is unauthenticated by design — it takes telemetry from a surface
that may have no session yet, so it cannot be gated. What it must not do is let
the caller choose what the record says about identity. It did:

```python
tenant_id: Optional[str] = "platform"      # in the request body
...
tenant_id=payload.tenant_id or "platform"
```

This is the same defect W0-C removed from the tenant header, where *"an omitted
header silently granted the platform scope"* — surviving in a second place,
wearing a value instead of an absence.

**W0-G sharpened its consequence.** Every audit write is now chained, so an event
forged through this endpoint is correctly hashed and the chain verifies as
`VERIFIED`. The integrity proof would lend the forgery its own credibility. A
tamper-evident log is only as trustworthy as the authority of what enters it.

Fixed by removing `tenant_id` from the payload model entirely: tenant now comes
from the session when one exists and is `UNATTRIBUTED` otherwise — a sentinel
chosen so it cannot collide with a real scope. Claimed `actor_id` and
`actor_role` are prefixed `client-asserted:`, so no member of `VALID_ROLES` can
ever match a value that entered here.

Six controls added in `test_audit_probe_authority.py`, including that the
endpoint still works without a session — a fix that broke the telemetry it was
protecting would not be a fix.

### W0-H

CLEAN. The static write-authority check operates over source files and has no
tenant dimension to omit; the seller-identity migration adds columns to a table
whose tenant scope is carried by its parent record.

## The guard, and the shape it missed

The estate guard was written first against `= None`. It found one candidate —
`seed_user(tenant_id=None)` — which is **not** a bypass: it is a data constructor
where `None` means the identity holds no tenant, and `require_tenant()` fails
closed on exactly that with `403 NO_TENANT_AUTHORITY`. Allowlisted with that
reason.

The `"platform"` default was invisible to it. A hard-coded scope is the same
defect wearing a value, and a guard looking only for `None` walks past it. The
guard now catches both, and a meta-test plants each shape to prove it.

```
TENANT_STATIC_GUARD_RESULT=PASS (1 allowlisted, reasoned)
TENANT_STATIC_GUARD_PERTURBATION=PASS — planted None default, planted "platform"
  default, and four spellings (tenant_id / tenantId / TENANT_ID / tenant) each detected
```

## C3 — F3 needle

```
F3_NEEDLE_DISPOSITION=CASE_INSENSITIVE
```

The retired-role guard matched `pharmacy_operator` case-sensitively. A live grant
reintroduced as `PHARMACY_OPERATOR` would have been invisible — and six existing
occurrences already were, including an entire
`GO_LIVE_CLOSURES/pharmacy_operator_confirmation/` directory. All are now
registered.

Two wrong turns are recorded because each is a way this repair could have been
made worse:

**Separator-optional matching.** Making the underscore optional as well as the
case matched the ordinary English phrase *"pharmacy operator"* across the
governance prose — 18 false positives. That would have driven the exclusion list
to grow until the guard meant nothing. A wire role keeps its underscore; only its
case can drift, so the underscore stays required.

**File-wide exemption.** Registering `main.py` and `access_control.py` as
display-only excluded those files entirely — and a planted
`PROBE_ROLE = "PHARMACY_OPERATOR"` in `main.py` then went undetected. The
exemption is now token-wise: the registered symbol `ROLE_PHARMACY_OPERATOR` is
subtracted from the text and the remainder is still scanned.

**Prose is stripped, literals are kept.** W0-D's own comment says
*"PHARMACY_OPERATOR is deliberately ABSENT"*; a guard flagging that would be
flagging the record of the retirement. Comments and docstrings are removed before
scanning, string literals are not — because a role in a literal is what a grant
looks like.

`ROLE_PHARMACY_OPERATOR = "Pharmacy Operator"` remains in coverage and is
registered with the reason it confers nothing: it is excluded from `VALID_ROLES`,
and `test_t_disp_05_retired_pharmacy_operator_cannot_authenticate` asserts that
exclusion. The symbol exists in order to be proven powerless.

```
F3_PERTURBATION_RESULT=PASS
  probe A  PROBE_ROLE = "PHARMACY_OPERATOR"  in petcare_api        -> FAILED (caught)
  probe B  PROBE = "Pharmacy_Operator"       in petcare_runtime    -> FAILED (caught)
  probe C  "# note: PHARMACY_OPERATOR was retired by W0-D"         -> passed (correctly silent)
```

Probe C is the one that makes the disposition trustworthy: a guard that fired on
prose would be retrained away by its own false positives.

## Boundary

```
PRODUCTION_MUTATED=NO   LIVE_DB_MUTATED=NO
GCP_MUTATED=NO          EXTERNAL_DASHBOARD_MUTATED=NO
PACKAGE_SCOPE_REOPENED=NO — W0-G/W0-H logic unchanged except the /audit/ui defect
```
