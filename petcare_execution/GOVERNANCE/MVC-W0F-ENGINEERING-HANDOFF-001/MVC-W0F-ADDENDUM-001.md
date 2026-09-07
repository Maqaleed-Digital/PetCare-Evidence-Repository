# MVC-W0F-ADDENDUM-001 — governed correction to the W0-F handoff pack

**Status:** append-only addendum · **Date:** 2026-09-07 · **Authority:** Sponsor
**Governs:** `MVC-W0F-ENGINEERING-HANDOFF-001`, whose text is **not modified**.

This addendum records four changes of state since the pack was written. The pack
itself is sealed: nothing in it is edited, and where this addendum and the pack
disagree, the pack remains the historical record and this addendum is the current
determination.

---

## 1 · D.21 residency — Sponsor authority

Verbatim:

> "Portfolio precedent may establish the temporary operating location, but not
> the final residency destination. MyVetiCare may remain out of Kingdom until the
> approved KSA hosting site is ready, at which point migration to KSA becomes
> mandatory."

```
D21_CURRENT_STATE=TEMPORARY_OUT_OF_KINGDOM_ALLOWED
D21_TARGET_STATE=KSA_MIGRATION_MANDATORY_WHEN_APPROVED_KSA_SITE_READY
D21_PORTFOLIO_PRECEDENT=TEMPORARY_OPERATING_LOCATION_ONLY
D21_PERMANENT_RESIDENCY_PRECEDENT=NO
```

### The distinction this ruling turns on

Two authorities were previously conflated, and separating them is the whole point
of the ruling:

| | |
|---|---|
| **CURRENT_OPERATION_AUTHORITY** | Where MyVetiCare may run *today*. Satisfied by the approved Maqaleed portfolio operating posture. Temporary by construction. |
| **TARGET_RESIDENCY_AUTHORITY** | Where MyVetiCare data must *finally* reside. Not yet satisfied. Becomes binding when the approved KSA hosting site is ready. |

Portfolio precedent supplies the first and **does not** supply the second. The
W0-F readiness lane had earlier flagged that sibling projects run in
`me-central-1` (UAE) while MyVetiCare is a KSA product under PDPL; that flag is
now answered — the sibling region is an acceptable *temporary operating
location*, and is not, and does not become, the permanent residency authority.

### What this ruling explicitly does NOT say

Recorded because each is a reading the ruling could be stretched into:

- It does **not** say KSA residency is already active.
- It does **not** make current out-of-Kingdom hosting permanent.
- It does **not** make UAE or any sibling region the permanent residency
  authority for MyVetiCare.
- It does **not** conclude that current hosting is legally compliant merely
  because portfolio precedent exists. Compliance of the temporary posture is a
  separate question this ruling does not reach.

### The engineering consequence

Migration to KSA is a **scheduled certainty, not a contingency**. That changes how
the serving layer must be built: hosting location is configuration, never
semantics. See `MVC-W0F-KSA-MIGRATION-READINESS-001`.

---

## 2 · Acceptance criterion 8 — SATISFIED

The pack lists as open:

> 8. Password storage uses a memory-hard KDF; no bare SHA-256 survives.

```
W0F_AC8=SATISFIED_BY_W0J_SCRYPT
```

W0-J (PR #14, merged 2026-09-07T10:41:26Z) replaced `_hash_password` with salted,
work-factored `hashlib.scrypt`, parameters stored in the hash, plus a
rehash-on-next-login path for legacy formats. Verified live in
`petcare_api/routers/auth.py`, and guarded by `petcare_api/tests/test_password_kdf.py`
(T-PW-01), whose static check inspects the calls `_hash_password` makes.

AC-8 is removed from active W0-F residue in future summaries. **The pack's
historical text is unchanged** — it was accurate when written.

---

## 3 · Agent implementation boundary — superseded for non-production scope

The pack's status line reads `W0_F_AGENT_IMPLEMENTATION=NO`, with *"No agent lane
may implement it."* That flag is recorded here as **superseded for the
non-production scope only**, by Sponsor direction of 2026-09-07, and the reasoning
is set down so the supersession is auditable rather than assumed.

The pack gave three grounds. Their current state:

| Ground | State |
|---|---|
| "It requires a production data decision — which store, in which region, under which residency authority. Residency is unresolved (`D.21 OPEN`)." | **RESOLVED.** D.21 ruled above; store decision taken in `MVC-W0F-DATA-STORE-DECISION-001`. |
| "It requires migration of live identity, which is irreversible." | **EXCLUDED.** Migration is prepared and dry-run only. Applying it remains `GATE_IRREVERSIBLE_ACTION` + `GATE_LIVE_APPLY`. |
| "It is the substrate for every security control in Wave-0. A subtle error does not fail a test, it silently widens authorization." | **STANDS, and is not dismissed.** |

The third ground is not resolved by any ruling, because it is a statement about
the nature of the work rather than about missing authority. It is answered by
method instead: every control added under this addendum is an armed negative
control, each perturbation must fail for its intended reason, and a guard that
passes without a demonstrated failing perturbation is not accepted as evidence.
That is a mitigation, not a refutation — a reviewer should read the W0-F
implementation with the pack's warning in mind.

```
W0F_AGENT_IMPLEMENTATION=NON_PRODUCTION_ONLY_BY_SPONSOR_DIRECTION_2026-09-07
W0F_PRODUCTION_IMPLEMENTATION=SPONSOR_GATED (unchanged)
```

Authorising authority: CP-2, `Ratified`, decision date 2026-08-31, lodged
2026-09-07, immutable — which authorises *"Wave-0 engineering changes in
non-production branches and environments only"*.

---

## 4 · Remaining W0-F scope

With AC-8 closed and D.21 ruled, the remaining scope is:

```
1  production serving data-store        decided here; provisioning is gated
2  AC-7 session revocation              designed and implemented non-production
3  governed secret source               decided here; secret entry is gated
4  identity migration                   prepared and dry-run only; apply is gated
5  KSA target migration readiness       specified here; execution is future
```

Items 1–3 and 5 are completable without crossing a gate. Item 4 is completable
only up to the dry-run boundary.

---

## Referenced artefacts

```
MVC-W0F-DATA-STORE-DECISION-001          data-store architecture decision
MVC-W0F-KSA-MIGRATION-READINESS-001      KSA migration readiness specification
MVC-W0F-IDENTITY-MIGRATION-PLAN-001      identity migration plan (prepare only)
```
