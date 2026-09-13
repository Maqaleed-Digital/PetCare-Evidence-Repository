# MVC-EXECUTION-RULES-REGISTER-001 — the canonical standing-rules register

**Established:** 2026-09-13 · **Status:** ACTIVE

**Governing acts**

| rules | act | date |
|---|---|---|
| 13–17 | `[SPONSOR]` *MYVETICARE EXECUTION RULES 13–17* — §4 below | 13 September 2026 |
| 18–24 | `[SPONSOR]` *MYVETICARE EXECUTION RULES 18–24* — §5 below | 13 September 2026 |

This is the **single canonical register** of MyVetiCare standing execution and
evidence rules. Where any receipt, evidence bundle, request or summary disagrees
with this register about what a rule *is*, this register governs.

It does **not** govern what a rule *was*. See §7.

```
REGISTER_STATUS=ACTIVE
RULES_RATIFIED=13,14,15,16,17,18,19,20,21,22,23,24
RULES_UNDEFINED_UNRATIFIED=1,2,3,4,5,6,7,8,9,10,11,12
P1_AUTHORIZED=NO
GATE_LIVE_APPLY=NOT_AUTHORIZED
GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
```

---

## 1 — Status summary

| Rule | Canonical key | Status |
|---|---|---|
| 13 | `GREEN_CI_NECESSARY_NOT_SUFFICIENT` | **RATIFIED** 2026-09-13 |
| 14 | `NARRATIVE_IS_NOT_LIVE_STATE` | **RATIFIED** 2026-09-13 |
| 15 | `INTEGRITY_IS_NOT_AUTHORITY` | **RATIFIED** 2026-09-13 |
| 16 | `REACHABILITY_IS_PART_OF_DELIVERY` | **RATIFIED** 2026-09-13 |
| 17 | `PERTURBATION_ACQUISITION_MUST_BE_PROVEN_BEFORE_ADJUDICATION` | **RATIFIED** 2026-09-13 |
| 18 | `LIVE_RESIDUE_REMEASUREMENT` | **RATIFIED** 2026-09-13 |
| 19 | `FALSE_POSITIVE_INTEGRITY_CONTROLS` | **RATIFIED** 2026-09-13 |
| 20 | `SPONSOR_AUTHORITY` | **RATIFIED** 2026-09-13 |
| 21 | `ABSENCE_OVER_VALIDATION` | **RATIFIED** 2026-09-13 |
| 22 | `REPEATED_PROCESS_FAILURE_BECOMES_A_CONTROL` | **RATIFIED** 2026-09-13 |
| 23 | `GENESIS_CASE` | **RATIFIED** 2026-09-13 |
| 24 | `LAYERED_DEFENCE_PERTURBATION` | **RATIFIED** 2026-09-13 |

Rules **1–12** remain undefined and unratified. No definition of any of them
exists in this repository and none is cited by any artefact. Recorded so their
absence is a known fact rather than an unexamined gap.

---

## 2 — Superseded keys · historical aliases

The Rules 13–17 ruling names each rule afresh, so four canonical keys differ
from the shorthands already in circulation. The earlier keys are **retained and
resolvable**, not deleted: 15 sealed receipts and evidence bundles use them, and
both rulings forbid silently rewriting a historical record.

| superseded key | → canonical key | where it appears |
|---|---|---|
| `LIVE_REGISTER_OUTRANKS_NARRATIVE` | `NARRATIVE_IS_NOT_LIVE_STATE` | 7 artefacts, 2026-09-12 |
| `LIVE_REGISTER_OUTRANKS_TRUNCATED_TRANSCRIPT` | `NARRATIVE_IS_NOT_LIVE_STATE` | 4 artefacts, 2026-09-07 |
| `WRITE_AUTHORITY_PRECEDES_INTEGRITY_CHAIN` | `INTEGRITY_IS_NOT_AUTHORITY` | receipts + bundles |
| `CONTROL_DELIVERED_ONLY_WHEN_GOVERNED_PATH_REACHES_IT` | `REACHABILITY_IS_PART_OF_DELIVERY` | receipts + bundles |
| `PERTURBATION_PROVEN_APPLIED_BEFORE_ADJUDICATION` | `PERTURBATION_ACQUISITION_MUST_BE_PROVEN_BEFORE_ADJUDICATION` | 3 bundles, latest `20260912T140000Z` |
| `PERTURBATION_MUST_BE_PROVEN_APPLIED_BEFORE_ADJUDICATION` | `PERTURBATION_ACQUISITION_MUST_BE_PROVEN_BEFORE_ADJUDICATION` | 2 bundles, latest `20260912T100000Z` |
| `RESIDUE_REMEASURED_FROM_LIVE_SOURCE` | `LIVE_RESIDUE_REMEASUREMENT` | receipts + bundles |
| `NO_FALSE_TAMPER_FINDING_UNDER_CORRECT_OPERATION` | `FALSE_POSITIVE_INTEGRITY_CONTROLS` | receipts + bundles |

`GREEN_CI_NECESSARY_NOT_SUFFICIENT` is unchanged and needs no alias.

### How the two recorded conflicts were resolved

Both were resolved by **supersession, not selection**. The register previously
recorded a Rule 14 conflict (`…NARRATIVE` vs `…TRUNCATED_TRANSCRIPT`) and a
Rule 17 wording variance, with recommendations deliberately left unselected
because selecting them is a Sponsor act. The ruling did not adopt either side of
either conflict — it named both rules afresh, and both prior variants now map to
a single canonical key.

* **Rule 14** — the ruled scope is the broader one. *Narrative* covers any
  receipt, transcript, handoff, summary or historical decision record, not only
  a truncated one, which is the harder and more common failure.
* **Rule 17** — `MUST BE` is normative rather than descriptive, and the subject
  is **acquisition**: whether the intended change actually landed. That is a
  sharper statement of the property than "proven applied", and it is the exact
  question `P-07a`/`P-08a` turned on.

```
RULE_14_CONFLICT=RESOLVED_BY_SUPERSESSION
RULE_17_CONFLICT=RESOLVED_BY_SUPERSESSION
```

---

## 3 — Boundaries between neighbouring rules

Recorded so the boundaries are stated rather than inferred.

**Rule 17 and Rule 24** are complementary, not duplicates. Rule 17 asks *did the
perturbation actually land?*; Rule 24 asks *which layer actually held the
property?* A perturbation can satisfy 17 and still leave 24 unresolved — which is
precisely what happened at `P-07a`/`P-08a`, where the perturbation demonstrably
landed and the control stayed green because a deeper layer was holding.

**Rule 15 and Rule 20** are the same principle at two levels. Rule 15 says an
integrity record does not establish that its writer had authority; Rule 20 says
decisive wording does not establish that its author was the Sponsor. Both refuse
to let a well-formed artefact stand in for the authority behind it.

**Rule 13 and Rule 16** meet at vacuity. Rule 13 rejects a passing gate that did
not measure its governed scope; Rule 16 rejects a control no governed path
invokes. A control that exists but is unreachable will produce exactly the
passing gate Rule 13 refuses to accept.

---

## 4 — The Rules 13–17 ruling, verbatim

> ```
> [SPONSOR RULING — MYVETICARE EXECUTION RULES 13–17]
>
> Date: 13 September 2026
>
> I ratify the following as standing MyVetiCare execution and evidence rules.
>
> RULE 13 — GREEN CI IS NECESSARY, NOT SUFFICIENT
>
> Green CI is necessary but is never sufficient by itself for merge, acceptance,
> or production-readiness determination.
>
> Acceptance also requires complete evidence, armed and non-vacuous controls,
> required perturbation proof, reconciliation of material test/coverage counts,
> and disposition of material findings.
>
> A passing gate that did not measure its governed scope is not evidence of
> acceptance.
>
> RULE 14 — NARRATIVE IS NOT LIVE STATE
>
> A narrative artefact — including a receipt, transcript, handoff, summary,
> historical decision record, or other account of prior state — is not itself the
> current register or current system state.
>
> Before execution or adjudication, live repository, register, PR, infrastructure,
> or other authoritative state must be verified where available.
>
> Where live authoritative state and prior narrative differ, the live state
> governs, while the prior narrative remains historical evidence and must not be
> silently rewritten.
>
> RULE 15 — INTEGRITY IS NOT AUTHORITY
>
> A hash chain, digest, signature, immutable record, sealed bundle, or other
> integrity mechanism proves properties about the integrity or provenance of a
> record after it was written.
>
> It does not by itself prove that the actor who wrote or caused the record to be
> written had authority to do so.
>
> Write authority must be established independently before the resulting record
> is treated as governed authority.
>
> RULE 16 — REACHABILITY IS PART OF DELIVERY
>
> An implemented control, authorization check, repository, guard, or other
> mechanism is not considered delivered solely because code for it exists.
>
> A governed serving or execution path must demonstrably reach the mechanism in
> the conditions where the control is claimed to apply.
>
> A control that no governed path invokes is operationally equivalent to an
> absent control for acceptance purposes.
>
> RULE 17 — PERTURBATION ACQUISITION MUST BE PROVEN BEFORE ADJUDICATION
>
> Before the result of a perturbation or mutation test is adjudicated, acquisition
> of the intended perturbation MUST BE independently proven.
>
> Proof must establish that the intended change actually landed in the relevant
> scope before the control result is interpreted.
>
> Acceptable evidence may include a content check, marker, diff, structural
> inspection, or another independent acquisition proof appropriate to the change.
>
> If acquisition is not proven, a green result is not evidence of a vacuous
> control and a red result is not evidence that the intended perturbation was
> detected.
>
> The perturbation must be corrected or re-applied and the control re-run before
> adjudication.
>
> GOVERNANCE
>
> These rules take effect from this Sponsor ruling.
>
> Prior receipts and artefacts that cited Rules 13–17 before this ruling remain
> historical records of the execution reasoning used at the time.
>
> This ruling does not retroactively represent those earlier citations as having
> possessed Sponsor authority when they did not.
>
> No historical receipt, sealed evidence bundle, or provenance record is to be
> silently rewritten to imply otherwise.
>
> Rules 18–24 remain governed by their existing ratification.
>
> Rules 1–12 remain undefined and unratified unless separately governed later.
>
> This ruling does not authorize any production mutation, credential entry,
> production genesis execution, production tenant creation, production identity
> creation, serving binding, or cutover.
>
> P1_AUTHORIZED=NO
> GATE_LIVE_APPLY=NOT_AUTHORIZED
> GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
>
> [SPONSOR]
> ```

---

## 5 — The Rules 18–24 ruling, verbatim

> ```
> [SPONSOR RULING — MYVETICARE EXECUTION RULES 18–24]
>
> I ratify the following as standing execution and evidence rules for MyVetiCare.
>
> RULE 18 — LIVE RESIDUE REMEASUREMENT
> Residue classification must be re-measured from live source at the start of
> every lane. A classification recorded by a prior receipt is evidence of the
> prior state, not proof of the current state.
>
> RULE 19 — FALSE-POSITIVE INTEGRITY CONTROLS
> An integrity mechanism that produces false positives under ordinary operation
> is defective. Integrity controls must distinguish legitimate operation from
> tamper conditions reliably enough that ordinary operation does not train
> operators to disregard genuine alerts.
>
> RULE 20 — SPONSOR AUTHORITY
> Analysis, recommendation, drafted wording, agent output, or implementation does
> not constitute a Sponsor ruling regardless of how decisively it is phrased.
>
> A Sponsor decision becomes authority only through an explicit Sponsor act.
>
> No agent may ratify, approve, authorize, or sign a Sponsor decision on the
> Sponsor's behalf.
>
> RULE 21 — ABSENCE OVER VALIDATION
> Where an input, parameter, capability, or authority is unnecessary, prefer
> removing it from the governed interface rather than accepting and validating
> it.
>
> An absent capability cannot be defaulted, passed incorrectly, relaxed by a
> later validation change, or used as an unintended escalation path.
>
> This rule does not prohibit post-condition or defence-in-depth controls where
> they protect the resulting invariant.
>
> RULE 22 — REPEATED PROCESS FAILURE BECOMES A CONTROL
> When the same material process omission or coverage failure occurs three times,
> it must no longer depend on operator memory or procedural discipline alone.
>
> A durable control must be introduced.
>
> The corrective control must not make the gate self-assembling in a way that
> removes an explicit human decision about what belongs in scope.
>
> RULE 23 — GENESIS CASE
> Every governance model that depends on an already-authorized actor must be
> examined for its genesis case.
>
> Correct steady-state controls must not be assumed to provide authority for the
> first actor.
>
> Where genesis authority is required, it must be explicitly governed before the
> system depends on it.
>
> RULE 24 — LAYERED-DEFENCE PERTURBATION
> A control that remains green after removal of the precondition or defence it is
> claimed to test is unresolved, not automatically proven.
>
> Layered defences must be perturbed independently until the control responsible
> for holding the property is identified.
>
> Perturbation evidence must record the mechanism that actually held the
> property, including ineffective first probes, rather than attributing success
> to a layer that was not load-bearing.
>
> GOVERNANCE
>
> These rules take effect as standing MyVetiCare execution rules from this
> Sponsor ruling.
>
> Prior receipts that cited Rules 18–24 before this ruling remain historical
> records of the execution reasoning used at the time. This ruling does not
> retroactively represent those citations as having possessed Sponsor authority
> when they did not.
>
> No historical receipt, sealed evidence bundle, or provenance record is to be
> silently rewritten to imply otherwise.
>
> This ruling does not itself authorize any production mutation, credential
> entry, production genesis execution, production tenant creation, production
> identity creation, serving binding, or cutover.
>
> P1_AUTHORIZED=NO
> GATE_LIVE_APPLY=NOT_AUTHORIZED
> GATE_CREDENTIAL_ENTRY=NOT_AUTHORIZED
>
> Date: 13 September 2026
> [SPONSOR]
> ```

---

## 6 — Effect on `REQUEST-002`

All twelve rules the request adjudicates are now governed. Its adjudication
block is updated to the canonical keys, the `ungoverned` qualifier on Rules
13–17 is removed, and each is re-adjudicated against the **ratified** text
rather than the drafted text it was written against.

Rule 13's ratified wording is broader than the draft — it additionally requires
*reconciliation of material test/coverage counts* and *disposition of material
findings*. The request already satisfies both: CI's 882 passed / 7 skipped is
reconciled explicitly against local 889 / 0 and against the 847 + 7 baseline,
and the material finding of this lane (the stale 39-migration abort condition)
is disposed of in plan revision 2.

```
REQUEST_002_ADJUDICATION_BASIS=FULLY_GOVERNED
EVIDENCE_BASE_SHA=UNCHANGED
PLAN_SHA256=UNCHANGED
REQUEST_002_ACTION=AMENDED_IN_PLACE_NOT_REISSUED
```

A reissue would be required only if the evidence base or the plan digest moved.
Neither did — this register adds no code, no migration and no test.

---

## 7 — Provenance · prospective effect, no retroactive laundering

```
RULES_13_17_EFFECTIVE_FROM=2026-09-13
RULES_18_24_EFFECTIVE_FROM=2026-09-13
RETROACTIVE_AUTHORITY=NONE
HISTORICAL_RECEIPTS_REWRITTEN=0
SEALED_BUNDLES_MODIFIED=0
SUPERSEDED_KEYS_DELETED=0
```

Every receipt and evidence bundle that cited Rules 13–24 before 2026-09-13 did
so **without Sponsor authority**, because none existed. Those citations record
the execution reasoning genuinely used at the time, and they remain exactly as
written.

No receipt was edited, no sealed bundle was re-hashed, and no digest was
recomputed to imply those rules were governed when they were not. Establishing
and extending this register creates authority **forward**; it does not reach
backwards, and the earlier documents continue to tell the truth about their own
provenance.

The superseded keys in §2 are retained for the same reason. Rewriting a sealed
artefact to use a key ratified after it was sealed would make it assert an
authority it did not have — the precise thing both rulings forbid.

---

## 8 — Open, for a future Sponsor act

```
RULES_1_12=NO_DEFINITION_EXISTS
GITHUB_SUPPORT_REFS_PULL_1_6=NOT_SENT — proposed as a hard cutover condition;
                                        NOT covered by either ruling
```

`refs/pull/1–6` was deliberately kept out of both rulings: it is a release
control, not an execution rule, and combining it with execution-rule
ratification would blur two different authorities. It is recorded here as an
open item, not as a rule, and still requires its own act.

Nothing in this register authorizes any production act. The two outstanding
production authorizations remain separate:

```
REQUEST_002           P1 phases B-D    GATE_LIVE_APPLY + GATE_CREDENTIAL_ENTRY
P1_GENESIS_STEP_001   first platform_admin genesis, one time only
```
